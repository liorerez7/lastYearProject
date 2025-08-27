import React, { useState, useMemo } from 'react';
import DEMO_RESULTS from './demoResults';


import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import { Zap, Users, Filter, X } from 'lucide-react';

export default function PerformanceChart({ results }) {
  const [metricType, setMetricType] = useState("avg");
  const [selectedUserLevel, setSelectedUserLevel] = useState(null);


  results = DEMO_RESULTS;

  // Extract user levels and create friendly names
  const { userLevels, chartData } = useMemo(() => {
    const extractUserCount = (testName) => {
      const match = testName.match(/(\d+)u/);
      return match ? parseInt(match[1]) : null;
    };

    const generateFriendlyName = (testName, queryType) => {
      const userCount = extractUserCount(testName);
      const baseType = testName.replace(/_\d+u$/, '').replace(/_/g, ' ');
      const formattedQueryType = queryType?.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()) || 'Unknown';

      // Create a more descriptive name
      const typeMap = {
      'lookup': 'Point Lookups',
      'dash': 'Dashboard Reads',
      'smalljoin': 'Simple Joins',
      'smoke': 'General Load Test',
      'index': 'Index Efficiency Test',
      'mix': 'Mixed Workload Simulation',
      'rw': 'Read-Write Heavy',
      'report': 'Reporting & Analytics',
      'edge': 'Edge Case & Recursive Queries',
      'heavy': 'Heavy Operations & Joins',
      'spike30': 'High Load Spike (30 Users)'
    };


      const friendlyType = typeMap[baseType.toLowerCase()] || baseType.charAt(0).toUpperCase() + baseType.slice(1);

      return {
        shortName: userCount ? `${formattedQueryType} (${userCount}u)` : formattedQueryType,
        fullName: userCount ? `${friendlyType} - ${formattedQueryType} (${userCount} users)` : `${friendlyType} - ${formattedQueryType}`,
        userCount
      };
    };

    // Get unique user levels
    const levels = [...new Set(results.map(r => extractUserCount(r.test_name)).filter(Boolean))].sort((a, b) => a - b);

    // Filter results by selected user level
    const filteredResults = selectedUserLevel
      ? results.filter(r => extractUserCount(r.test_name) === selectedUserLevel)
      : results;

    // Transform data for chart
    const data = filteredResults.map(result => {
      const friendlyNames = generateFriendlyName(result.test_name, result.query_type);
      const userCount = extractUserCount(result.test_name);

      let mysqlValue = result.mysql_avg_duration;
      let pgValue = result.postgres_avg_duration;

      if (metricType === "p95") {
        mysqlValue = result.mysql_p95;
        pgValue = result.postgres_p95;
      } else if (metricType === "stddev") {
        mysqlValue = result.mysql_stddev;
        pgValue = result.postgres_stddev;
      }

      return {
        name: friendlyNames.shortName,
        fullName: friendlyNames.fullName,
        originalTestName: result.test_name,
        MySQL: mysqlValue,
        PostgreSQL: pgValue,
        queryType: result.query_type.replace(/_/g, " "),
        winner: result.winner,
        userCount,
        // Include all metrics for tooltip
        mysql_avg: result.mysql_avg_duration,
        postgres_avg: result.postgres_avg_duration,
        mysql_p95: result.mysql_p95,
        postgres_p95: result.postgres_p95,
        mysql_stddev: result.mysql_stddev,
        postgres_stddev: result.postgres_stddev,
        mysql_count: result.mysql_count,
        postgres_count: result.postgres_count,
        difference_percent: result.difference_percent
      };
    });

    return { userLevels: levels, chartData: data };
  }, [results, metricType, selectedUserLevel]);

  const LoadLevelFilter = ({ userLevels, selectedLevel, onLevelChange }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700"
        >
          <Users size={14} />
          <span>
            {selectedLevel ? `${selectedLevel} Users` : 'All Loads'}
          </span>
          <span className="text-gray-400 text-xs">▼</span>
        </button>

        {isOpen && (
          <div className="absolute top-full right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-[140px]">
            <div className="p-2">
              <button
                onClick={() => {
                  onLevelChange(null);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-3 py-2 rounded-md hover:bg-gray-100 transition-colors flex items-center gap-2 text-sm ${
                  !selectedLevel ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700'
                }`}
              >
                <Users size={12} />
                All Loads
                {!selectedLevel && <span className="ml-auto text-blue-600 text-xs">✓</span>}
              </button>
              {userLevels.map(level => (
                <button
                  key={level}
                  onClick={() => {
                    onLevelChange(level);
                    setIsOpen(false);
                  }}
                  className={`w-full text-left px-3 py-2 rounded-md hover:bg-gray-100 transition-colors flex items-center gap-2 text-sm ${
                    selectedLevel === level ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700'
                  }`}
                >
                  <Users size={12} />
                  {level}u
                  {selectedLevel === level && <span className="ml-auto text-blue-600 text-xs">✓</span>}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;

      return (
        <div className="p-4 border shadow-lg rounded-xl bg-white opacity-98 max-w-sm">
          <div className="mb-3 pb-2 border-b">
            <p className="text-base font-bold text-gray-800">{data.fullName}</p>
            {data.userCount && (
              <div className="flex items-center gap-1 mt-1">
                <Users size={12} className="text-gray-500" />
                <span className="text-xs text-gray-600">{data.userCount} concurrent users</span>
              </div>
            )}
          </div>

          <div className="space-y-3">
            {/* Current Metric Values */}
            <div>
              <div className="text-xs font-medium text-gray-600 mb-2">
                {metricType === "avg" ? "Average Duration" : metricType === "p95" ? "95th Percentile" : "Standard Deviation"}
              </div>
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center text-blue-600">
                  <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                  <span className="font-medium">MySQL:</span>
                </div>
                <span className="font-bold">{payload[0]?.value?.toFixed(3)}s</span>
              </div>
              <div className="flex items-center justify-between text-sm mt-1">
                <div className="flex items-center text-green-600">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  <span className="font-medium">PostgreSQL:</span>
                </div>
                <span className="font-bold">{payload[1]?.value?.toFixed(3)}s</span>
              </div>
            </div>

            {/* Performance Summary */}
            {data.winner !== 'Tie' && (
              <div className="bg-gray-50 p-2 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">Performance Winner</div>
                <div className={`text-sm font-medium ${data.winner === 'MySQL' ? 'text-blue-600' : 'text-green-600'}`}>
                  {data.winner} is {data.difference_percent.toFixed(1)}% faster
                </div>
              </div>
            )}

            {/* Variability Metrics - Always show regardless of current metric */}
            <div className="border-t pt-2">
              <div className="text-xs font-medium text-gray-600 mb-2">Query Variability</div>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <div className="text-blue-600 font-medium mb-1">MySQL</div>
                  <div className="space-y-0.5">
                    <div>Avg: {data.mysql_avg?.toFixed(3)}s</div>
                    <div>P95: {data.mysql_p95?.toFixed(3)}s</div>
                    <div>σ: {data.mysql_stddev?.toFixed(3)}s</div>
                    <div className="text-gray-500">{data.mysql_count} runs</div>
                  </div>
                </div>
                <div>
                  <div className="text-green-600 font-medium mb-1">PostgreSQL</div>
                  <div className="space-y-0.5">
                    <div>Avg: {data.postgres_avg?.toFixed(3)}s</div>
                    <div>P95: {data.postgres_p95?.toFixed(3)}s</div>
                    <div>σ: {data.postgres_stddev?.toFixed(3)}s</div>
                    <div className="text-gray-500">{data.postgres_count} runs</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  // Color coding for different user loads
  const getUserLoadColor = (userCount) => {
    const colors = {
      5: { mysql: '#1e40af', postgres: '#059669' },   // Darker blue/green
      10: { mysql: '#3b82f6', postgres: '#10b981' },  // Medium blue/green
      15: { mysql: '#60a5fa', postgres: '#34d399' },  // Lighter blue/green
      20: { mysql: '#93c5fd', postgres: '#6ee7b7' },  // Very light blue/green
    };
    return colors[userCount] || { mysql: '#6b7280', postgres: '#9ca3af' }; // Gray fallback
  };

  return (
    <div className="card bg-white shadow-xl border-2 border-gray-200">
      <div className="card-body p-6">
        <div className="flex flex-wrap justify-between items-center mb-6 gap-4">
          <div>
            <h2 className="card-title text-xl md:text-2xl flex items-center gap-2">
              <Zap size={24} className="text-blue-600" />
              Performance Comparison
            </h2>
            {selectedUserLevel && (
              <p className="text-sm text-gray-600 mt-1">
                Showing results for {selectedUserLevel} concurrent users
              </p>
            )}
          </div>

          <div className="flex items-center gap-3">
            {selectedUserLevel && (
              <button
                onClick={() => setSelectedUserLevel(null)}
                className="flex items-center gap-2 px-3 py-2 bg-red-50 text-red-700 border border-red-200 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium"
              >
                <X size={14} />
                Clear
              </button>
            )}

            <LoadLevelFilter
              userLevels={userLevels}
              selectedLevel={selectedUserLevel}
              onLevelChange={setSelectedUserLevel}
            />

            <div className="form-control">
              <label className="label text-sm font-medium text-gray-600 pb-1">
                Metric:
              </label>
              <select
                className="select select-sm select-bordered"
                value={metricType}
                onChange={(e) => setMetricType(e.target.value)}
              >
                <option value="avg">Average</option>
                <option value="p95">95th Percentile</option>
                <option value="stddev">Std Deviation</option>
              </select>
            </div>
          </div>
        </div>

        {chartData.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-500 text-lg mb-2">No data to display</div>
            <div className="text-gray-400 text-sm">
              {selectedUserLevel
                ? `No tests found for ${selectedUserLevel} user load level`
                : 'No benchmark results available'
              }
            </div>
          </div>
        ) : (
          <div className="h-96 w-full bg-gradient-to-br from-gray-50 to-white rounded-lg p-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                margin={{ top: 5, right: 10, left: 10, bottom: 85 }}
              >
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis
                  dataKey="name"
                  angle={-45}
                  textAnchor="end"
                  interval={0}
                  tick={{ fontSize: 11, fill: '#444' }}
                  height={85}
                />
                <YAxis
                  label={{
                    value:
                      metricType === "avg"
                        ? "Average Duration (s)"
                        : metricType === "p95"
                        ? "95th Percentile (s)"
                        : "Standard Deviation (s)",
                    angle: -90,
                    position: "insideLeft",
                    style: { textAnchor: "middle", fontSize: 12, fill: "#555" },
                    dy: 10,
                    dx: 0
                  }}
                  tick={{ fontSize: 11, fill: '#444' }}
                  tickFormatter={(value) => value.toFixed(1)}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="top" height={36} />
                <Bar
                  dataKey="MySQL"
                  fill="#3b82f6"
                  name="MySQL"
                  radius={[4, 4, 0, 0]}
                  barSize={selectedUserLevel ? 16 : 12}
                  isAnimationActive={true}
                  animationDuration={1500}
                />
                <Bar
                  dataKey="PostgreSQL"
                  fill="#10b981"
                  name="PostgreSQL"
                  radius={[4, 4, 0, 0]}
                  barSize={selectedUserLevel ? 16 : 12}
                  isAnimationActive={true}
                  animationDuration={1500}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Legend for user load levels when showing all loads */}
        {!selectedUserLevel && userLevels.length > 1 && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg border">
            <div className="text-xs font-medium text-gray-600 mb-2">User Load Levels in Dataset:</div>
            <div className="flex flex-wrap gap-2">
              {userLevels.map(level => (
                <button
                  key={level}
                  onClick={() => setSelectedUserLevel(level)}
                  className="flex items-center gap-1 px-2 py-1 bg-white border border-gray-200 rounded-md hover:bg-blue-50 hover:border-blue-300 transition-colors text-xs"
                >
                  <Users size={10} />
                  <span>{level} users</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}