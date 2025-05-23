import React, { useState } from 'react';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, Tooltip } from 'recharts';
import { TrendingUp, Code, Eye, EyeOff, Info, Users, Activity } from 'lucide-react';

export default function QueryTypeComparison({ results = [] }) {
  const [showSQLModal, setShowSQLModal] = useState(false);
  const [selectedQuery, setSelectedQuery] = useState(null);

  // Handle empty or undefined results
  if (!results || results.length === 0) {
    return (
      <div className="card bg-white shadow-xl border border-gray-200 p-8">
        <div className="text-center text-gray-500">
          <TrendingUp className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium mb-2">No Query Data Available</h3>
          <p>No query performance results to display.</p>
        </div>
      </div>
    );
  }

  const queryTypes = [...new Set(results.map(r => r.query_type).filter(Boolean))];

  // Calculate load level ranges
  const loadLevels = results.map(r => r.load_level).filter(Boolean);
  const minLoad = loadLevels.length > 0 ? Math.min(...loadLevels) : 0;
  const maxLoad = loadLevels.length > 0 ? Math.max(...loadLevels) : 0;
  const loadRange = loadLevels.length > 0 ? `${minLoad}–${maxLoad} users` : 'Variable load';

  const radarData = queryTypes.map(type => {
  const typeResults = results.filter(r => r.query_type === type);
  const mysqlAvg = typeResults.length > 0 ? typeResults.reduce((sum, r) => sum + (r.mysql_avg_duration || 0), 0) / typeResults.length : 0;
  const postgresAvg = typeResults.length > 0 ? typeResults.reduce((sum, r) => sum + (r.postgres_avg_duration || 0), 0) / typeResults.length : 0;

  const mysqlWins = typeResults.filter(r => r.winner === 'MySQL').length;
  const pgWins = typeResults.filter(r => r.winner === 'PostgreSQL').length;

  const lowLoadResults = typeResults.filter(r => r.load_level && r.load_level <= (maxLoad * 0.4));
  const highLoadResults = typeResults.filter(r => r.load_level && r.load_level >= (maxLoad * 0.7));

  const mysqlLowLoadWins = lowLoadResults.filter(r => r.winner === 'MySQL').length;
  const mysqlHighLoadWins = highLoadResults.filter(r => r.winner === 'MySQL').length;
  const pgLowLoadWins = lowLoadResults.filter(r => r.winner === 'PostgreSQL').length;
  const pgHighLoadWins = highLoadResults.filter(r => r.winner === 'PostgreSQL').length;

  // ✅ Use sql_queries directly (from backend)
  const uniqueQueries = new Set();
  console.log("🔍 [QueryTypeComparison] Processing query_type:", type);
  typeResults.forEach(result => {
    console.log("📦 [QueryTypeComparison] result.sql_queries:", result.sql_queries);
    if (result.sql_queries && Array.isArray(result.sql_queries)) {
      result.sql_queries.forEach(query => {
        if (query && query.trim()) {
          uniqueQueries.add(query);
          console.log("✅ [QueryTypeComparison] Using query from sql_queries:", query);
        }
      });
    }

    // Second: fallback – extract from json_data if still empty
    if (uniqueQueries.size === 0 && Array.isArray(result.json_data)) {
      result.json_data.forEach(item => {
        if (item && item.query && item.query.trim()) {
          uniqueQueries.add(item.query);
          console.log("✅ [QueryTypeComparison] Fallback: Using query from json_data:", item.query);
        }
      });
    }
  });

  const sampleQueries = Array.from(uniqueQueries);
  if (sampleQueries.length === 0) {
    sampleQueries.push(`-- Sample ${formatQueryType(type)} Query\nSELECT * FROM table WHERE condition = 'example';`);
  }

  function formatQueryType(type) {
    return type
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  }

  return {
    displayType: formatQueryType(type),
    MySQL: mysqlAvg,
    PostgreSQL: postgresAvg,
    mysqlWins,
    pgWins,
    fasterDB: mysqlAvg < postgresAvg ? 'MySQL' : mysqlAvg > postgresAvg ? 'PostgreSQL' : 'Tie',
    totalTests: typeResults.length,
    loadContext: {
      mysqlLowLoadWins,
      mysqlHighLoadWins,
      pgLowLoadWins,
      pgHighLoadWins,
      lowLoadTotal: lowLoadResults.length,
      highLoadTotal: highLoadResults.length
    },
    uniqueQueryCount: sampleQueries.length,
    sampleQueries
  };
});


  function getLoadContextText(data) {
    const { mysqlLowLoadWins, mysqlHighLoadWins, pgLowLoadWins, pgHighLoadWins, lowLoadTotal, highLoadTotal } = data.loadContext;

    if (lowLoadTotal === 0 && highLoadTotal === 0) return '';

    if (data.fasterDB === 'MySQL') {
      if (mysqlLowLoadWins > mysqlHighLoadWins && lowLoadTotal > 0) {
        return '(mostly under low load)';
      } else if (mysqlHighLoadWins > mysqlLowLoadWins && highLoadTotal > 0) {
        return '(mostly under high load)';
      }
    } else if (data.fasterDB === 'PostgreSQL') {
      if (pgLowLoadWins > pgHighLoadWins && lowLoadTotal > 0) {
        return '(mostly under low load)';
      } else if (pgHighLoadWins > pgLowLoadWins && highLoadTotal > 0) {
        return '(mostly under high load)';
      }
    }

    return '(across all loads)';
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="p-5 border shadow-xl rounded-lg bg-white opacity-98 max-w-sm">
          <p className="text-lg font-bold text-gray-800 mb-2">{data.displayType}</p>
          <div className="h-px bg-gray-200 mb-3"></div>

          <div className="grid grid-cols-2 gap-3 mb-3">
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
              <p className="text-xs text-blue-600 font-semibold mb-1">MySQL Avg. Time</p>
              <p className="text-xl font-bold text-blue-800">{data.MySQL.toFixed(3)}s</p>
            </div>

            <div className="bg-green-50 p-3 rounded-lg border border-green-200">
              <p className="text-xs text-green-600 font-semibold mb-1">PostgreSQL Avg. Time</p>
              <p className="text-xl font-bold text-green-800">{data.PostgreSQL.toFixed(3)}s</p>
            </div>
          </div>

          <div className="bg-gray-50 p-3 rounded-lg border border-gray-200 mb-3">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Load Range: {loadRange}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-blue-600">MySQL wins: <span className="font-semibold">{data.mysqlWins}</span></span>
              <span className="text-green-600">PostgreSQL wins: <span className="font-semibold">{data.pgWins}</span></span>
            </div>
          </div>

          <div className="text-center">
            {data.fasterDB !== 'Tie' ? (
              <div className="flex items-center justify-center gap-2">
                <Activity className="w-4 h-4" />
                <span className={`font-semibold ${data.fasterDB === 'MySQL' ? 'text-blue-700' : 'text-green-700'}`}>
                  {data.fasterDB} performs better {getLoadContextText(data)}
                </span>
              </div>
            ) : (
              <span className="text-gray-600 font-medium">Performance is comparable</span>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  const handleShowSQL = (queries) => {
    setSelectedQuery(queries);
    setShowSQLModal(true);
  };

  return (
    <>
      <div className="card bg-white shadow-2xl border border-gray-100">
        <div className="card-body p-8">
          <div className="flex flex-wrap justify-between items-center mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-green-500 rounded-lg">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl md:text-3xl font-bold text-gray-800">Query Type Performance Analysis</h2>
                <p className="text-sm text-gray-600 mt-1 flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  Load range: {loadRange} • {results.length} total tests
                </p>
              </div>
            </div>
          </div>

          <div className="h-[450px] w-full bg-gradient-to-br from-gray-50 via-blue-50/30 to-green-50/30 rounded-xl p-6 shadow-inner border border-gray-100">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart outerRadius="78%" data={radarData}>
                <PolarGrid stroke="#d1d5db" strokeWidth={1} />
                <PolarAngleAxis
                  dataKey="displayType"
                  tick={{ fontSize: 12, fill: '#374151', fontWeight: 500 }}
                />
                <PolarRadiusAxis
                  angle={30}
                  domain={[0, 'auto']}
                  tick={{ fontSize: 10, fill: '#6b7280' }}
                  tickFormatter={(value) => `${value.toFixed(1)}s`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Radar
                  name="MySQL"
                  dataKey="MySQL"
                  stroke="#2563eb"
                  fill="#3b82f6"
                  fillOpacity={0.4}
                  strokeWidth={3}
                  isAnimationActive={true}
                  animationDuration={2000}
                />
                <Radar
                  name="PostgreSQL"
                  dataKey="PostgreSQL"
                  stroke="#059669"
                  fill="#10b981"
                  fillOpacity={0.4}
                  strokeWidth={3}
                  isAnimationActive={true}
                  animationDuration={2000}
                />
                <Legend
                  wrapperStyle={{fontSize: "14px", color: '#374151', fontWeight: 500}}
                  iconType="rect"
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mt-8">
            {radarData.map((data, index) => (
              <div
                key={index}
                className={`relative overflow-hidden bg-gradient-to-br ${
                  data.fasterDB === 'MySQL' ? 'from-blue-50 via-blue-50/70 to-white border-blue-200 shadow-blue-100' :
                  data.fasterDB === 'PostgreSQL' ? 'from-green-50 via-green-50/70 to-white border-green-200 shadow-green-100' :
                  'from-gray-50 via-gray-50/70 to-white border-gray-200 shadow-gray-100'
                } p-5 rounded-xl border-2 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105`}
              >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-bold text-base text-gray-800 leading-tight">{data.displayType}</h3>
                  <div className="flex items-center gap-1">
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full font-medium">
                      {data.uniqueQueryCount} SQL {data.uniqueQueryCount === 1 ? 'query' : 'queries'}
                    </span>
                    <button
                      onClick={() => handleShowSQL(data.sampleQueries)}
                      className="p-1.5 hover:bg-white/60 rounded-lg transition-colors group"
                      title={`View ${data.uniqueQueryCount} SQL ${data.uniqueQueryCount === 1 ? 'query' : 'queries'}`}
                    >
                      <Code className="w-4 h-4 text-gray-500 group-hover:text-gray-700" />
                    </button>
                  </div>
                </div>

                <div className={`flex items-center gap-2 mb-3 ${
                  data.fasterDB === 'MySQL' ? 'text-blue-700' :
                  data.fasterDB === 'PostgreSQL' ? 'text-green-700' :
                  'text-gray-700'
                }`}>
                  <TrendingUp className="w-5 h-5" />
                  <span className="font-bold text-lg">
                    {data.fasterDB !== 'Tie' ? data.fasterDB : 'Equal'}
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-blue-700">MySQL</span>
                    <span className="text-sm font-bold text-blue-800">{data.MySQL.toFixed(3)}s</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-green-700">PostgreSQL</span>
                    <span className="text-sm font-bold text-green-800">{data.PostgreSQL.toFixed(3)}s</span>
                  </div>
                </div>

                <div className="text-xs text-gray-600 mb-3">
                  <div className="flex items-center gap-1 mb-1">
                    <Users className="w-3 h-3" />
                    <span>Load range: {loadRange}</span>
                  </div>
                  <div>
                    Based on <span className="font-semibold">{data.totalTests}</span> tests
                  </div>
                  {data.fasterDB !== 'Tie' && (
                    <div className="mt-1 font-medium text-gray-700">
                      {data.fasterDB} wins {data.fasterDB === 'MySQL' ? data.mysqlWins : data.pgWins} tests {getLoadContextText(data)}
                    </div>
                  )}
                </div>

                <div className="relative w-full bg-gray-200 rounded-full h-2.5 overflow-hidden mb-2">
                  <div
                    className="absolute top-0 left-0 h-full bg-blue-500 transition-all duration-1000"
                    style={{ width: `${((data.mysqlWins / ((data.mysqlWins + data.pgWins) || 1)) * 100).toFixed(1)}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-600 mb-1">
                  <span className="font-medium">MySQL: {data.mysqlWins} wins</span>
                  <span className="font-medium">PostgreSQL: {data.pgWins} wins</span>
                </div>
                <div className="text-center">
                  <span className="text-xs text-gray-500">
                    {data.mysqlWins + data.pgWins === 0 ? 'No winners recorded' :
                     Math.round((data.mysqlWins / (data.mysqlWins + data.pgWins)) * 100)}% MySQL wins
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* SQL Query Modal */}
      {showSQLModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex justify-between items-center p-6 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-100 rounded-lg">
                  <Code className="w-5 h-5 text-gray-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-800">SQL Queries</h3>
                  <p className="text-sm text-gray-600">
                    {Array.isArray(selectedQuery) ? selectedQuery.length : 1} unique {Array.isArray(selectedQuery) && selectedQuery.length === 1 ? 'query' : 'queries'} for this type
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowSQLModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <EyeOff className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            <div className="p-6 max-h-[60vh] overflow-y-auto">
              {Array.isArray(selectedQuery) ? (
                <div className="space-y-6">
                  {selectedQuery.map((query, index) => (
                    <div key={index}>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-1 rounded-full">
                          Query #{index + 1}
                        </span>
                        {selectedQuery.length > 1 && (
                          <span className="text-xs text-gray-500">
                            of {selectedQuery.length} unique queries
                          </span>
                        )}
                      </div>
                      <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                        <pre className="text-green-400 text-sm font-mono whitespace-pre-wrap">
                          {query}
                        </pre>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                  <pre className="text-green-400 text-sm font-mono whitespace-pre-wrap">
                    {selectedQuery}
                  </pre>
                </div>
              )}
              <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-start gap-2">
                  <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div className="text-sm text-blue-800">
                    <p className="font-medium mb-1">Query Analysis Information</p>
                    <p>
                      {Array.isArray(selectedQuery) && selectedQuery.length > 1
                        ? `These ${selectedQuery.length} unique queries were tested for this query type. Performance results are averaged across all variations.`
                        : 'This query represents the SQL statement tested for this query type. Performance results may include multiple runs with different parameters.'
                      }
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}