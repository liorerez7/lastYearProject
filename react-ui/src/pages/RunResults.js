import React, { useState, useMemo } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "react-query";
import axios from "axios";

// Icons from the new code
import { LayoutGrid, BarChartBig, FileText, Info as InfoIcon, AlertCircle, Bolt, ArrowRight, ScanLine, Users, Filter, X, Timer } from "lucide-react";

// Components from your original ("old") code structure
import BenchmarkCard from "../components/BenchmarkCard";
import BenchmarkSummary from "../components/BenchmarkSummary";
import PerformanceChart from "../components/PerformanceChart";
import QueryTypeComparison from "../components/QueryTypeComparison";

// API URL from your old code
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8080";

// Data fetching function from your old code
const getExecutions = async (test_id) => {
  const res = await axios.get(`${API_URL}/executions?test_id=${test_id}`);
  return res.data;
};

// Data transformation function from your old code
const transformExecutionData = (executions) => {


  const normalizeQuery = (query) => {
    return query
      .replace(/`/g, '"')           // שנה backticks לציטוט כפול
      .replace(/\s+/g, ' ')         // הסר רווחים כפולים
      .trim();                      // הסר רווחים בתחילה ובסוף
  };

  if (!executions || executions.length === 0) return [];
  console.log("🔄 [transformExecutionData] Raw executions:", executions);
  const groupedByQuery = executions.reduce((acc, exec) => {
    console.log("🔎 FULL EXEC OBJECT:", exec);
    const key = `${exec.test_type}_${exec.query_type}`;
    if (!acc[key]) {
      acc[key] = {
        test_type: exec.test_type,
        query_type: exec.query_type,
        schema: exec.schema,
        // NEW: Collect all SQL queries for this group
        sql_queries: new Set(),
        // NEW: Store load level information
        load_levels: new Set()
      };
    }

    // NEW: Add SQL query if it exists
    if (exec.sql_query) {
      acc[key].sql_queries.add(exec.sql_query);
      console.log(`✅ [transformExecutionData] Added sql_query for ${key}:`, exec.sql_query);
    }else {
        console.log("⚠️ [transformExecutionData] NO exec.sql_query for", exec.test_type, exec.db_type);
    }

    // NEW: Add any query from json_data if it exists
    if (exec.queries && Array.isArray(exec.queries)) {
  console.log("📥 [transformExecutionData] found queries in", exec.test_type, exec.db_type, exec.queries);

  exec.queries.forEach(item => {
    if (item && item.query && item.query.trim()) {
      const normalized = normalizeQuery(item.query);
      acc[key].sql_queries.add(normalized);
      console.log("✅ [transformExecutionData] added normalized query:", normalized);
    }
  });
} else {
  console.warn("⚠️ [transformExecutionData] NO queries field for", exec.test_type, exec.db_type);
}



    // NEW: Add load level information (using selector as load indicator based on your data)
    if (exec.selector !== undefined && exec.selector !== null) {
      acc[key].load_levels.add(exec.selector);
    }

    acc[key][exec.db_type] = exec;
    return acc;
  }, {});

  return Object.entries(groupedByQuery)
    .filter(([_, group]) =>
      group.mysql &&
      group.postgres &&
      (group.mysql.avg || 0) > 0 &&
      (group.postgres.avg || 0) > 0
    )
    .map(([key, group]) => {
      const mysql = group.mysql;
      const postgres = group.postgres;
      const mysqlAvg = mysql.avg || 0;
      const postgresAvg = postgres.avg || 0;

      const mysqlCount = mysql.executions_count || 0;
      const postgresCount = postgres.executions_count || 0;

      let winner = 'Tie';
      if (mysqlAvg !== postgresAvg) {
        winner = mysqlAvg < postgresAvg ? 'MySQL' : 'PostgreSQL';
      }

      let difference_percent = 0;
      if (winner !== 'Tie') {
        const fasterAvg = Math.min(mysqlAvg, postgresAvg);
        const slowerAvg = Math.max(mysqlAvg, postgresAvg);
        difference_percent = fasterAvg > 0 ? ((slowerAvg - fasterAvg) / fasterAvg) * 100 : 100;
      }

      return {
        test_name: group.test_type || key,
        mysql_avg_duration: mysqlAvg,
        postgres_avg_duration: postgresAvg,
        mysql_stddev: mysql.stddev || 0,
        postgres_stddev: postgres.stddev || 0,
        mysql_p95: mysql.p95 || 0,
        postgres_p95: postgres.p95 || 0,
        mysql_count: mysqlCount,
        postgres_count: postgresCount,
        query_type: group.query_type || 'N/A',
        difference_percent,
        winner,
        schema: group.schema,
        // NEW: Add the SQL queries and load information
        sql_queries: Array.from(group.sql_queries),
        load_level: group.load_levels.size > 0 ? Math.max(...Array.from(group.load_levels)) : 0,
        // NEW: Store original execution data for more detailed analysis
        json_data: mysql.json_data || postgres.json_data || null
      };
    });
};

// Filter Component
function LoadLevelFilter({ userLevels, selectedLevel, onLevelChange }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-colors font-medium text-gray-700"
      >
        <Filter size={16} />
        <span>
          {selectedLevel ? `${selectedLevel} Users` : 'All Load Levels'}
        </span>
        <span className="ml-1 text-gray-400">▼</span>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-[200px]">
          <div className="p-2">
            <button
              onClick={() => {
                onLevelChange(null);
                setIsOpen(false);
              }}
              className={`w-full text-left px-3 py-2 rounded-md hover:bg-gray-100 transition-colors flex items-center gap-2 ${
                !selectedLevel ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700'
              }`}
            >
              <Users size={14} />
              All Load Levels
              {!selectedLevel && <span className="ml-auto text-blue-600">✓</span>}
            </button>
            {userLevels.map(level => (
              <button
                key={level}
                onClick={() => {
                  onLevelChange(level);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-3 py-2 rounded-md hover:bg-gray-100 transition-colors flex items-center gap-2 ${
                  selectedLevel === level ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700'
                }`}
              >
                <Users size={14} />
                {level} Users
                {selectedLevel === level && <span className="ml-auto text-blue-600">✓</span>}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Tab Content Components
function TabOverviewContent({ results }) {
  const [selectedUserLevel, setSelectedUserLevel] = useState(null);

  // Extract user levels and filter results
  const { userLevels, filteredResults } = useMemo(() => {
    const extractUserCount = (testName) => {
      const match = testName.match(/(\d+)u/);
      return match ? parseInt(match[1]) : null;
    };

    const levels = [...new Set(results.map(r => extractUserCount(r.test_name)).filter(Boolean))].sort((a, b) => a - b);

    const filtered = selectedUserLevel
      ? results.filter(r => extractUserCount(r.test_name) === selectedUserLevel)
      : results;

    return { userLevels: levels, filteredResults: filtered };
  }, [results, selectedUserLevel]);

  const mysqlWins = filteredResults.filter(r => r.winner === 'MySQL').length;
  const pgWins = filteredResults.filter(r => r.winner === 'PostgreSQL').length;
  const totalTests = filteredResults.length;

  return (
    <div className="p-4 md:p-6">
      {/* Header with stats and filter */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
        <div className="flex flex-wrap items-stretch gap-3">
          <div className="flex-1 min-w-[180px] rounded-xl border border-blue-200 bg-gradient-to-r from-blue-50 to-blue-100 p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-200 rounded-lg">
                <Bolt size={20} className="text-blue-700" />
              </div>
              <div>
                <div className="text-sm font-semibold text-blue-700">MySQL Wins</div>
                <div className="text-2xl font-bold text-blue-800">{mysqlWins}</div>
                <div className="text-xs text-blue-600 mt-0.5">
                  {totalTests > 0 ? `${((mysqlWins / totalTests) * 100).toFixed(1)}% of tests` : '0% of tests'}
                </div>
              </div>
            </div>
          </div>

          <div className="flex-1 min-w-[180px] rounded-xl border border-green-200 bg-gradient-to-r from-green-50 to-green-100 p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-200 rounded-lg">
                <Bolt size={20} className="text-green-700" />
              </div>
              <div>
                <div className="text-sm font-semibold text-green-700">PostgreSQL Wins</div>
                <div className="text-2xl font-bold text-green-800">{pgWins}</div>
                <div className="text-xs text-green-600 mt-0.5">
                  {totalTests > 0 ? `${((pgWins / totalTests) * 100).toFixed(1)}% of tests` : '0% of tests'}
                </div>
              </div>
            </div>
          </div>

          <div className="flex-1 min-w-[180px] rounded-xl border border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100 p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gray-200 rounded-lg">
                <ScanLine size={20} className="text-gray-700" />
              </div>
              <div>
                <div className="text-sm font-semibold text-gray-700">Total Tests</div>
                <div className="text-2xl font-bold text-gray-800">{totalTests}</div>
                <div className="text-xs text-gray-600 mt-0.5">
                  {selectedUserLevel ? `${selectedUserLevel} user load` : 'All load levels'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-3">
          {selectedUserLevel && (
            <button
              onClick={() => setSelectedUserLevel(null)}
              className="flex items-center gap-2 px-3 py-2 bg-red-50 text-red-700 border border-red-200 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium"
            >
              <X size={14} />
              Clear Filter
            </button>
          )}
          <LoadLevelFilter
            userLevels={userLevels}
            selectedLevel={selectedUserLevel}
            onLevelChange={setSelectedUserLevel}
          />
        </div>
      </div>

      {/* Results */}
      {filteredResults.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg mb-2">No results found</div>
          <div className="text-gray-400 text-sm">
            {selectedUserLevel
              ? `No tests found for ${selectedUserLevel} user load level`
              : 'No benchmark results available'
            }
          </div>
        </div>
      ) : (
        <div className="max-h-[calc(100vh-280px)] overflow-y-auto pr-1 space-y-8">
          {[...new Set(filteredResults.map(r => r.query_type))].map((type, idx) => {
            const group = filteredResults.filter(r => r.query_type === type);
            const formattedType = type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

            return (
              <div key={idx} className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-white rounded-lg shadow-sm">
                    <Timer size={20} className="text-gray-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-800">{formattedType}</h3>
                    <p className="text-sm text-gray-600">{group.length} test{group.length !== 1 ? 's' : ''}</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                  {group.map((result, i) => (
                    <BenchmarkCard key={`${type}-${i}`} result={result} />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function TabChartsContent({ results }) {
  const mysqlLeadPercentage = results.length > 0 ? (results.filter(r => r.winner === 'MySQL').length / results.length) * 100 : 0;
  const pgLeadPercentage = results.length > 0 ? (results.filter(r => r.winner === 'PostgreSQL').length / results.length) * 100 : 0;
  const tiePercentage = results.length > 0 ? (results.filter(r => r.winner === 'Tie').length / results.length) * 100 : 0;

  // Get top performers for each database
  const topMySQLWins = results
    .filter(r => r.winner === 'MySQL')
    .sort((a, b) => b.difference_percent - a.difference_percent)
    .slice(0, 5);

  const topPostgreSQLWins = results
    .filter(r => r.winner === 'PostgreSQL')
    .sort((a, b) => b.difference_percent - a.difference_percent)
    .slice(0, 5);

  const generateFriendlyName = (testName, queryType) => {
    const userCount = testName.match(/(\d+)u/)?.[1];
    const baseType = testName.replace(/_\d+u$/, '').replace(/_/g, ' ');
    const formattedQueryType = queryType?.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()) || 'Unknown';

    const typeMap = {
      'smoke': 'Performance Test',
      'lookup': 'Data Lookup',
      'insert': 'Insert Operation',
      'update': 'Update Operation',
      'delete': 'Delete Operation',
      'complex': 'Complex Query'
    };

    const friendlyType = typeMap[baseType.toLowerCase()] || baseType.charAt(0).toUpperCase() + baseType.slice(1);

    return userCount ? `${friendlyType} - ${formattedQueryType} (${userCount}u)` : `${friendlyType} - ${formattedQueryType}`;
  };

  return (
    <div className="p-4 md:p-6 space-y-8">
      {/* Enhanced Performance Chart */}
      <PerformanceChart results={results} />

      <div className="divider my-8">
        <div className="badge badge-lg bg-gradient-to-r from-blue-100 to-green-100 border-gray-300 py-3 px-6 text-gray-700 font-semibold">
          Performance Analysis
        </div>
      </div>

      {/* Overall Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-xl border border-blue-200 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-200 rounded-lg">
              <Bolt size={20} className="text-blue-700" />
            </div>
            <div>
              <div className="text-sm font-semibold text-blue-700">MySQL Dominance</div>
              <div className="text-2xl font-bold text-blue-800">{mysqlLeadPercentage.toFixed(1)}%</div>
              <div className="text-xs text-blue-600">of all benchmark tests</div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-xl border border-green-200 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-200 rounded-lg">
              <Bolt size={20} className="text-green-700" />
            </div>
            <div>
              <div className="text-sm font-semibold text-green-700">PostgreSQL Dominance</div>
              <div className="text-2xl font-bold text-green-800">{pgLeadPercentage.toFixed(1)}%</div>
              <div className="text-xs text-green-600">of all benchmark tests</div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-4 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gray-200 rounded-lg">
              <ScanLine size={20} className="text-gray-700" />
            </div>
            <div>
              <div className="text-sm font-semibold text-gray-700">Tied Results</div>
              <div className="text-2xl font-bold text-gray-800">{tiePercentage.toFixed(1)}%</div>
              <div className="text-xs text-gray-600">negligible differences</div>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Leaders */}
      <div className="bg-gradient-to-r from-blue-50 via-purple-50 to-green-50 p-6 rounded-xl shadow-md border border-gray-200">
        <h3 className="text-xl font-bold mb-6 flex items-center text-gray-800">
          <ScanLine className="mr-3 text-gray-600" size={24} />
          Top Performance Leaders
        </h3>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* MySQL Top Wins */}
          <div className="bg-white p-5 shadow-lg rounded-xl border border-blue-100">
            <div className="mb-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
                <span className="text-lg font-bold text-blue-700">MySQL Top Wins</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className="bg-gradient-to-r from-blue-400 to-blue-600 h-4 rounded-full transition-all duration-1000 ease-out shadow-sm"
                  style={{ width: `${Math.min(mysqlLeadPercentage, 100)}%` }}
                ></div>
              </div>
              <div className="text-sm text-gray-600 mt-2">
                Leading in <strong>{mysqlLeadPercentage.toFixed(0)}%</strong> of benchmarks
              </div>
            </div>

            <div className="space-y-3 max-h-64 overflow-y-auto pr-2">
              {topMySQLWins.length > 0 ? (
                topMySQLWins.map((result, idx) => (
                  <div key={`mysql-win-${idx}`} className="bg-blue-50 p-3 rounded-lg shadow-sm border border-blue-100 hover:shadow-md transition-shadow">
                    <div className="font-semibold text-blue-800 text-sm mb-1">
                      {generateFriendlyName(result.test_name, result.query_type)}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Performance advantage:</span>
                      <span className="text-sm font-bold text-blue-600">
                        {result.difference_percent.toFixed(1)}% faster
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      MySQL: {(result.mysql_avg_duration * 1000).toFixed(1)}ms •
                      PostgreSQL: {(result.postgres_avg_duration * 1000).toFixed(1)}ms
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-sm">No MySQL wins found</div>
                </div>
              )}
            </div>
          </div>

          {/* PostgreSQL Top Wins */}
          <div className="bg-white p-5 shadow-lg rounded-xl border border-green-100">
            <div className="mb-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                <span className="text-lg font-bold text-green-700">PostgreSQL Top Wins</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className="bg-gradient-to-r from-green-400 to-green-600 h-4 rounded-full transition-all duration-1000 ease-out shadow-sm"
                  style={{ width: `${Math.min(pgLeadPercentage, 100)}%` }}
                ></div>
              </div>
              <div className="text-sm text-gray-600 mt-2">
                Leading in <strong>{pgLeadPercentage.toFixed(0)}%</strong> of benchmarks
              </div>
            </div>

            <div className="space-y-3 max-h-64 overflow-y-auto pr-2">
              {topPostgreSQLWins.length > 0 ? (
                topPostgreSQLWins.map((result, idx) => (
                  <div key={`pg-win-${idx}`} className="bg-green-50 p-3 rounded-lg shadow-sm border border-green-100 hover:shadow-md transition-shadow">
                    <div className="font-semibold text-green-800 text-sm mb-1">
                      {generateFriendlyName(result.test_name, result.query_type)}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Performance advantage:</span>
                      <span className="text-sm font-bold text-green-600">
                        {result.difference_percent.toFixed(1)}% faster
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      PostgreSQL: {(result.postgres_avg_duration * 1000).toFixed(1)}ms •
                      MySQL: {(result.mysql_avg_duration * 1000).toFixed(1)}ms
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-sm">No PostgreSQL wins found</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function TabQueryTypesContent({ results }) {
  const uniqueQueryTypes = [...new Set(results.map(r => r.query_type))];

  return (
    <div className="p-4 md:p-6 space-y-8">
      <QueryTypeComparison results={results} />

      <div className="divider my-6 md:my-8">
        <div className="badge badge-lg bg-base-200 border-base-300 py-3 px-4">Detailed Breakdown by Query Type</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 md:gap-6">
        {uniqueQueryTypes.map(queryType => {
          const typeResults = results.filter(r => r.query_type === queryType);
          if (typeResults.length === 0) return null;

          const mysqlTypeWins = typeResults.filter(r => r.winner === 'MySQL').length;
          const pgTypeWins = typeResults.filter(r => r.winner === 'PostgreSQL').length;

          let leadDB = 'Tie';
          let leadColorClass = 'border-gray-200';
          let leadTextClass = 'text-gray-500';
          let leadBgGradient = 'from-gray-50 to-white';

          if (mysqlTypeWins > pgTypeWins) {
            leadDB = 'MySQL';
            leadColorClass = 'border-blue-200';
            leadTextClass = 'text-blue-600';
            leadBgGradient = 'from-blue-50 to-white';
          } else if (pgTypeWins > mysqlTypeWins) {
            leadDB = 'PostgreSQL';
            leadColorClass = 'border-green-200';
            leadTextClass = 'text-green-600';
            leadBgGradient = 'from-green-50 to-white';
          }

          return (
            <div key={queryType} className={`card bg-gradient-to-br ${leadBgGradient} shadow-md border ${leadColorClass} transition-all hover:shadow-lg`}>
              <div className="card-body p-4">
                <h3 className="card-title flex justify-between items-center text-base md:text-lg">
                  <span className="capitalize text-neutral-700 font-semibold">
                    {queryType.replace(/_/g, ' ')}
                  </span>
                  {leadDB !== 'Tie' && (
                    <div className={`badge badge-sm badge-outline ${leadColorClass} ${leadTextClass} font-medium`}>
                      {leadDB} Lead
                    </div>
                  )}
                </h3>

                <div className="divider my-1.5"></div>

                <ul className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
                  {typeResults.map((result, rIdx) => (
                    <li key={rIdx} className="py-1.5 px-2 flex justify-between items-center text-xs md:text-sm hover:bg-base-100/50 rounded transition-colors">
                      <span className="font-medium text-neutral-600 mr-2 truncate" title={result.test_name}>{result.test_name}</span>
                      <div className="flex items-center gap-1.5 flex-shrink-0">
                        <span className={`badge badge-sm ${result.winner === 'MySQL' ? 'badge-info text-blue-700 bg-blue-100 border-blue-300' : 'badge-ghost'}`}>
                          {result.mysql_avg_duration.toFixed(2)}s
                        </span>
                        <ArrowRight className="h-3 w-3 text-gray-400" />
                        <span className={`badge badge-sm ${result.winner === 'PostgreSQL' ? 'badge-success text-green-700 bg-green-100 border-green-300' : 'badge-ghost'}`}>
                          {result.postgres_avg_duration.toFixed(2)}s
                        </span>
                        {result.winner !== 'Tie' && result.difference_percent > 0.1 && (
                           <div className={`text-xs font-semibold ml-1 ${result.winner === 'MySQL' ? 'text-blue-600' : 'text-green-600'}`}>
                            ({result.difference_percent.toFixed(0)}%)
                          </div>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function TabSummaryContent({ results, rawExecutions }) { // Pass rawExecutions if BenchmarkSummary needs it
  return (
    <div className="p-4 md:p-6">
      <BenchmarkSummary results={results} rawExecutions={rawExecutions} />
    </div>
  );
}


export default function RunResults() {
  const { test_id } = useParams(); // From old code
  const [activeTabIndex, setActiveTabIndex] = useState(0); // From new code

  // useQuery for data fetching from old code
  const { data: executions, isLoading, isError, error } = useQuery(
    ["executions", test_id], // test_id from useParams
    () => getExecutions(test_id),
    {
      // Optional: react-query options like staleTime, cacheTime
      // staleTime: 5 * 60 * 1000, // 5 minutes
      // cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  );

  // useMemo for transforming data, from old code (adapted)
  const results = useMemo(() => {
    if (executions) {
      return transformExecutionData(executions);
    }
    return [];
  }, [executions]);

  // Loading state from old code, styled
  if (isLoading) return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4 md:p-6 flex flex-col items-center justify-center text-center" data-theme="corporate">
        <div className="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-12 w-12 mb-4 border-t-primary"></div>
        <h2 className="text-xl font-semibold text-primary">Loading Benchmark Data...</h2>
        <p className="text-neutral-focus">Fetching results for Test ID: {test_id}</p>
    </div>
  );

  // Error state from old code, styled
  if (isError) return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50 p-4 md:p-6 flex flex-col items-center justify-center text-center" data-theme="corporate">
        <AlertCircle size={48} className="text-error mb-4" />
        <h2 className="text-xl font-semibold text-error-content">Failed to Load Data</h2>
        <p className="text-neutral-focus mb-2">Could not retrieve results for Test ID: {test_id}.</p>
        {error && <p className="text-xs text-error bg-error/10 p-2 rounded-md">{error.message}</p>}
    </div>
  );

  // Handle case where results are empty after loading (e.g., no matching data)
  if (!isLoading && results.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50 p-4 md:p-6 flex flex-col items-center justify-center text-center" data-theme="corporate">
        <InfoIcon size={48} className="text-warning mb-4" />
        <h2 className="text-xl font-semibold text-warning-content">No Data Available</h2>
        <p className="text-neutral-focus">No benchmark comparison data found for Test ID: {test_id}.</p>
        <p className="text-sm text-neutral-focus/70 mt-1">This could be due to an invalid Test ID or incomplete test execution.</p>
      </div>
    );
  }

  // Extract schema name for the header, assuming it's consistent across results
  const schemaName = results.length > 0 ? (results[0].schema || "finalEmp") : "finalEmp"; // Default or from first result

  // Tabs definition from new code, content adapted from old code
  const tabs = [
    { name: "Overview", shortName: "Overview", icon: LayoutGrid, content: <TabOverviewContent results={results} /> },
    { name: "Detailed Charts", shortName: "Charts", icon: BarChartBig, content: <TabChartsContent results={results} /> },
    { name: "Query Type Analysis", shortName: "Query Types", icon: FileText, content: <TabQueryTypesContent results={results} /> },
    { name: "Summary & Insights", shortName: "Summary", icon: InfoIcon, content: <TabSummaryContent results={results} rawExecutions={executions} /> },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-2 sm:p-4 md:p-6" data-theme="corporate"> {/* data-theme from new code */}
      <div className="max-w-7xl lg:max-w-8xl mx-auto"> {/* Wider for large screens */}
        <header className="text-center py-6 md:py-8 mb-6 bg-white rounded-xl shadow-lg border-t-4 border-primary">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-primary">Database Performance Analysis</h1>
          <p className="text-sm text-neutral-500 mt-1">Test ID: <code className="bg-base-200 px-1.5 py-0.5 rounded">{test_id}</code></p>
          <div className="flex justify-center items-center gap-2 sm:gap-3 mt-2">
            <div className="badge badge-md sm:badge-lg badge-outline border-blue-400 text-blue-600">MySQL</div>
            <span className="text-md sm:text-lg font-bold text-neutral-500">vs</span>
            <div className="badge badge-md sm:badge-lg badge-outline border-green-400 text-green-600">PostgreSQL</div>
          </div>
          <p className="text-neutral-focus mt-2 text-sm">Schema: <code className="bg-base-200 px-2 py-0.5 rounded-md text-secondary">{schemaName}</code></p>
        </header>

        <div className="flex justify-center mb-6 overflow-x-auto gap-2 px-2">
          {tabs.map((tab, index) => {
            const isActive = activeTabIndex === index;
            return (
              <button
                key={index}
                onClick={() => setActiveTabIndex(index)}
                className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-full border transition-all duration-200
                  ${isActive
                    ? "border-blue-400 ring-2 ring-blue-200 bg-white text-blue-700"
                    : "border-gray-300 text-gray-600 hover:bg-base-200"}
                `}
              >
                <tab.icon size={16} />
                <span className="hidden sm:inline">{tab.name}</span>
                <span className="sm:hidden">{tab.shortName}</span>
              </button>
            );
          })}
        </div>

        <div className="bg-white rounded-xl shadow-xl min-h-[60vh] overflow-hidden">
          {tabs[activeTabIndex] && tabs[activeTabIndex].content}
        </div>

        <footer className="text-center mt-8 py-4">
            <p className="text-xs text-neutral-500">
                This report compares MySQL and PostgreSQL performance for Test ID: {test_id} on schema "{schemaName}".
            </p>
            <p className="text-xs text-neutral-400 mt-1">
                &copy; {new Date().getFullYear()} {"<Your Company Name / Project Name>"} All rights reserved.
            </p>
        </footer>
      </div>
    </div>
  );
}




