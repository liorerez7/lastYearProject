//import React from "react";
//import { useParams } from "react-router-dom";
//import { useQuery } from "react-query";
//import axios from "axios";
//
//const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8080";
//
//const getExecutions = async (test_id) => {
//  const res = await axios.get(`${API_URL}/executions?test_id=${test_id}`);
//  return res.data;
//};
//
//const RunResults = () => {
//  const { test_id } = useParams(); // שמנו בפרמטר של ה־URL
//  const { data, isLoading, isError } = useQuery(["executions", test_id], () => getExecutions(test_id));
//
//  if (isLoading) return <div>טוען תוצאות...</div>;
//  if (isError) return <div>שגיאה בטעינת התוצאות</div>;
//
//  return (
//    <div className="p-6">
//      <h1 className="text-xl font-bold mb-4">תוצאות גולמיות</h1>
//      <pre style={{ background: "#f0f0f0", padding: "1rem", overflowX: "auto" }}>
//        {JSON.stringify(data, null, 2)}
//      </pre>
//    </div>
//  );
//};
//
//export default RunResults;



import React, { useState, useMemo } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "react-query";
import axios from "axios";

// Icons from the new code
import { LayoutGrid, BarChartBig, FileText, Info as InfoIcon, AlertCircle, Bolt, ArrowRight, ScanLine } from "lucide-react"; // Renamed Info to InfoIcon to avoid conflict

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
// This function already calculates 'winner' and 'difference_percent'
// which are expected by your BenchmarkCard and BenchmarkSummary components.
const transformExecutionData = (executions) => {
  if (!executions || executions.length === 0) return [];

  const groupedByQuery = executions.reduce((acc, exec) => {
    // Using exec.test_type as primary key for grouping tests,
    // and adding query_type to distinguish if test_type is not unique across query_types
    const key = `${exec.test_type}_${exec.query_type}`;
    if (!acc[key]) {
      acc[key] = {
        // Store details from the first encountered record for this key
        test_type: exec.test_type,
        query_type: exec.query_type,
        schema: exec.schema // Assuming schema might be available
      };
    }
    acc[key][exec.db_type] = exec;
    return acc;
  }, {});

  return Object.entries(groupedByQuery)
    .filter(([_, group]) => group.mysql && group.postgres)
    .map(([key, group]) => {
      const mysql = group.mysql;
      const postgres = group.postgres;
      const mysqlAvg = mysql.avg || 0;
      const postgresAvg = postgres.avg || 0;

      let winner = 'Tie';
      if (mysqlAvg !== postgresAvg) { // Handle potential floating point inaccuracies if numbers are extremely close
          winner = mysqlAvg < postgresAvg ? 'MySQL' : 'PostgreSQL';
      }

      // Calculation of difference_percent based on the faster DB (from your old code)
      let difference_percent = 0;
      if (winner !== 'Tie') {
        const फास्टरAvg = Math.min(mysqlAvg, postgresAvg);
        const स्लोवरAvg = Math.max(mysqlAvg, postgresAvg);
        if (फास्टरAvg > 0) { // Avoid division by zero if faster is 0 (though unlikely for durations)
            difference_percent = ((स्लोवरAvg - फास्टरAvg) / फास्टरAvg) * 100;
        } else if (स्लोवरAvg > 0) { // If faster is 0 but slower is not, it's 100% difference
            difference_percent = 100;
        }
      }


      return {
        test_name: group.test_type || key, // Prefer test_type if available directly on group
        mysql_avg_duration: mysqlAvg,
        postgres_avg_duration: postgresAvg,
        query_type: group.query_type || 'N/A', // Prefer query_type from group
        difference_percent: difference_percent,
        winner,
        // Pass along schema if available for header or other uses
        schema: group.schema
      };
    });
};

// Tab Content Components (adapted from your old code's conditional rendering)

function TabOverviewContent({ results }) {
  const mysqlWins = results.filter(r => r.winner === 'MySQL').length;
  const pgWins = results.filter(r => r.winner === 'PostgreSQL').length;

  return (
    <div className="p-4 md:p-6">
      <div className="flex flex-wrap items-stretch gap-3 mb-6 md:mb-6">
        <div className="flex-1 min-w-[200px] rounded-lg border border-blue-200 bg-blue-50 p-3 shadow-sm">
          <div className="flex items-center gap-3">
            <Bolt size={20} className="text-blue-600" />
            <div>
              <div className="text-sm font-semibold text-blue-700">MySQL Wins</div>
              <div className="text-xl font-bold text-blue-800">{mysqlWins}</div>
              <div className="text-xs text-gray-500 mt-0.5">Tests where MySQL performed better</div>
            </div>
          </div>
        </div>

        <div className="flex-1 min-w-[200px] rounded-lg border border-green-200 bg-green-50 p-3 shadow-sm">
          <div className="flex items-center gap-3">
            <Bolt size={20} className="text-green-600" />
            <div>
              <div className="text-sm font-semibold text-green-700">PostgreSQL Wins</div>
              <div className="text-xl font-bold text-green-800">{pgWins}</div>
              <div className="text-xs text-gray-500 mt-0.5">Tests where PostgreSQL performed better</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 gap-4 md:gap-5">
        {results.map((result, idx) => (
          <BenchmarkCard key={idx} result={result} />
        ))}
      </div>
    </div>
  );
}

function TabChartsContent({ results }) {
  // This is the "Performance Distribution" section from your new code's TabCharts.
  // It's a bit different from just showing PerformanceChart.
  // We can include PerformanceChart and then this new distribution.
  const mysqlLeadPercentage = results.length > 0 ? (results.filter(r => r.winner === 'MySQL').length / results.length) * 100 : 0;
  const pgLeadPercentage = results.length > 0 ? (results.filter(r => r.winner === 'PostgreSQL').length / results.length) * 100 : 0;

  return (
    <div className="p-4 md:p-6 space-y-8">
      <PerformanceChart results={results} />

      <div className="divider my-6 md:my-8">
        <div className="badge badge-lg bg-base-200 border-base-300 py-3 px-4">Performance Distribution</div>
      </div>

      <div className="bg-gradient-to-r from-blue-50 via-purple-50 to-green-50 p-4 md:p-6 rounded-xl shadow-md border border-base-200">
        <h3 className="text-lg md:text-xl font-bold mb-4 flex items-center text-neutral-700">
          <ScanLine className="mr-2 opacity-70" />
          Database Lead in Tests
        </h3>

        <div className="flex flex-col md:flex-row gap-6">
          {/* MySQL Lead Section */}
          <div className="flex-1 card bg-white p-4 shadow rounded-lg border border-blue-100">
            <div className="mb-3 text-center">
              <span className="text-sm font-semibold text-blue-600">MySQL Performance Lead</span>
              <div className="w-full bg-gray-200 rounded-full h-3.5 my-1.5">
                <div
                  className="bg-blue-500 h-3.5 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${mysqlLeadPercentage}%` }}
                ></div>
              </div>
              <div className="text-xs text-gray-500">
                MySQL was faster in <strong>{mysqlLeadPercentage.toFixed(0)}%</strong> of tests
              </div>
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
              {results
                .filter(r => r.winner === 'MySQL')
                .slice(0, 4) // Show top few examples
                .map((result, idx) => (
                  <div key={`mysql-win-${idx}`} className="bg-blue-50 p-2.5 rounded-md shadow-sm border border-blue-100 text-xs">
                    <div className="font-medium text-blue-700">{result.test_name}</div>
                    <div className="text-gray-600 mt-0.5">
                      {result.difference_percent.toFixed(1)}% faster than PostgreSQL
                    </div>
                  </div>
                ))
              }
            </div>
          </div>

          {/* PostgreSQL Lead Section */}
          <div className="flex-1 card bg-white p-4 shadow rounded-lg border border-green-100">
            <div className="mb-3 text-center">
              <span className="text-sm font-semibold text-green-600">PostgreSQL Performance Lead</span>
              <div className="w-full bg-gray-200 rounded-full h-3.5 my-1.5">
                <div
                  className="bg-green-500 h-3.5 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${pgLeadPercentage}%` }}
                ></div>
              </div>
              <div className="text-xs text-gray-500">
                PostgreSQL was faster in <strong>{pgLeadPercentage.toFixed(0)}%</strong> of tests
              </div>
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
              {results
                .filter(r => r.winner === 'PostgreSQL')
                .slice(0, 4) // Show top few examples
                .map((result, idx) => (
                  <div key={`pg-win-${idx}`} className="bg-green-50 p-2.5 rounded-md shadow-sm border border-green-100 text-xs">
                    <div className="font-medium text-green-700">{result.test_name}</div>
                    <div className="text-gray-600 mt-0.5">
                      {result.difference_percent.toFixed(1)}% faster than MySQL
                    </div>
                  </div>
                ))
              }
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




