import React, { useState } from 'react';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { TrendingUp, BarChart2, PieChart } from 'lucide-react';

export default function QueryTypeComparison({ results }) {
  const [chartType, setChartType] = useState('radar'); // 'radar' or 'bar'

  const queryTypes = [...new Set(results.map(r => r.query_type))];

  const radarData = queryTypes.map(type => {
    const typeResults = results.filter(r => r.query_type === type);
    const mysqlAvg = typeResults.length > 0 ? typeResults.reduce((sum, r) => sum + (r.mysql_avg_duration || 0), 0) / typeResults.length : 0;
    const postgresAvg = typeResults.length > 0 ? typeResults.reduce((sum, r) => sum + (r.postgres_avg_duration || 0), 0) / typeResults.length : 0;

    // Add counts and which one is faster
    const mysqlWins = typeResults.filter(r => r.winner === 'MySQL').length;
    const pgWins = typeResults.filter(r => r.winner === 'PostgreSQL').length;

    return {
      queryType: type,
      MySQL: mysqlAvg,
      PostgreSQL: postgresAvg,
      displayType: formatQueryType(type),
      mysqlWins,
      pgWins,
      fasterDB: mysqlWins > pgWins ? 'MySQL' : pgWins > mysqlWins ? 'PostgreSQL' : 'Tie',
      totalTests: typeResults.length
    };
  });

  function formatQueryType(type) {
    return type
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase()); // Capitalize each word
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="p-4 border shadow-lg rounded-md bg-white opacity-95">
          <p className="text-base font-bold">{data.displayType}</p>
          <div className="divider my-1"></div>

          <div className="grid grid-cols-2 gap-4 mb-2">
            <div className="bg-blue-50 p-2 rounded border border-blue-100">
              <p className="text-xs text-blue-700 font-medium">MySQL Avg. Time</p>
              <p className="text-lg font-bold text-blue-800">{data.MySQL.toFixed(3)} s</p>
            </div>

            <div className="bg-green-50 p-2 rounded border border-green-100">
              <p className="text-xs text-green-700 font-medium">PostgreSQL Avg. Time</p>
              <p className="text-lg font-bold text-green-800">{data.PostgreSQL.toFixed(3)} s</p>
            </div>
          </div>

          <div className="mt-2 text-sm text-gray-600">
            <div className="flex justify-between">
              <span>MySQL wins: <span className="font-medium text-blue-700">{data.mysqlWins}</span></span>
              <span>PostgreSQL wins: <span className="font-medium text-green-700">{data.pgWins}</span></span>
            </div>
            <div className="mt-1 font-medium">
              {data.fasterDB !== 'Tie' ?
                <span className={data.fasterDB === 'MySQL' ? 'text-blue-700' : 'text-green-700'}>
                  {data.fasterDB} performs better on average
                </span> :
                <span className="text-gray-700">Performance is comparable</span>
              }
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card bg-white shadow-xl border-2 border-gray-200">
      <div className="card-body p-6">
        <div className="flex flex-wrap justify-between items-center mb-4">
          <h2 className="card-title text-xl md:text-2xl">Query Type Performance Analysis</h2>

          <div className="tabs tabs-boxed">
            <a
              className={`tab gap-1 ${chartType === 'radar' ? 'tab-active' : ''}`}
              onClick={() => setChartType('radar')}
            >
              <PieChart size={16} />
              Radar Chart
            </a>
            <a
              className={`tab gap-1 ${chartType === 'bar' ? 'tab-active' : ''}`}
              onClick={() => setChartType('bar')}
            >
              <BarChart2 size={16} />
              Bar Chart
            </a>
          </div>
        </div>

        <div className="h-96 w-full bg-gradient-to-br from-gray-50 to-white rounded-lg p-4">
          {chartType === 'radar' ? (
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart outerRadius="75%" data={radarData}>
                <PolarGrid stroke="#ccc" />
                <PolarAngleAxis
                  dataKey="displayType"
                  tick={{ fontSize: 11, fill: '#444' }}
                />
                <PolarRadiusAxis
                  angle={30}
                  domain={[0, 'auto']}
                  tick={{ fontSize: 10, fill: '#555' }}
                  tickFormatter={(value) => value.toFixed(1)}
                />
                <Tooltip content={<CustomTooltip />} />
                <Radar
                  name="MySQL"
                  dataKey="MySQL"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.5}
                  isAnimationActive={true}
                  animationDuration={1500}
                />
                <Radar
                  name="PostgreSQL"
                  dataKey="PostgreSQL"
                  stroke="#10b981"
                  fill="#10b981"
                  fillOpacity={0.5}
                  isAnimationActive={true}
                  animationDuration={1500}
                />
                <Legend wrapperStyle={{fontSize: "12px", color: '#555'}} />
              </RadarChart>
            </ResponsiveContainer>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={radarData}
                margin={{ top: 20, right: 30, left: 20, bottom: 70 }}
                barGap={0}
                barCategoryGap="20%"
              >
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis
                  dataKey="displayType"
                  tick={{ fontSize: 11, fill: '#444' }}
                  interval={0}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis
                  label={{
                    value: 'Avg. Duration (seconds)',
                    angle: -90,
                    position: 'insideLeft',
                    style: { textAnchor: 'middle', fontSize: 12, fill: '#555' },
                    dx: -15
                  }}
                  tickFormatter={(value) => value.toFixed(1)}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="top" height={36} />
                <Bar
                  dataKey="MySQL"
                  fill="#3b82f6"
                  name="MySQL"
                  radius={[4, 4, 0, 0]}
                  isAnimationActive={true}
                />
                <Bar
                  dataKey="PostgreSQL"
                  fill="#10b981"
                  name="PostgreSQL"
                  radius={[4, 4, 0, 0]}
                  isAnimationActive={true}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-6">
          {radarData.map((data, index) => (
            <div
              key={index}
              className={`stat bg-gradient-to-br ${
                data.fasterDB === 'MySQL' ? 'from-blue-50 to-white border-blue-200' :
                data.fasterDB === 'PostgreSQL' ? 'from-green-50 to-white border-green-200' :
                'from-gray-50 to-white border-gray-200'
              } p-4 rounded-lg border shadow-sm`}
            >
              <div className="stat-title text-sm capitalize">{data.displayType}</div>
              <div className={`stat-value text-sm ${
                data.fasterDB === 'MySQL' ? 'text-blue-600' :
                data.fasterDB === 'PostgreSQL' ? 'text-green-600' :
                'text-gray-600'
              }`}>
                <div className="flex items-center">
                  <TrendingUp className="mr-1" size={16} />
                  {data.fasterDB !== 'Tie' ? data.fasterDB : 'Equal'}
                </div>
              </div>
              <div className="stat-desc mt-1">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-blue-600">{data.MySQL.toFixed(2)}s</span>
                  <span className="text-gray-400">vs</span>
                  <span className="text-green-600">{data.PostgreSQL.toFixed(2)}s</span>
                </div>
                <div className="progress-bar h-1.5 rounded-full bg-gray-200 mt-1 overflow-hidden">
                  <div className="h-full bg-blue-500" style={{
                    width: `${(data.mysqlWins / (data.mysqlWins + data.pgWins || 1)) * 100}%`
                  }}></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}