import React, { useState } from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ScatterChart, ZAxis, Scatter, Cell } from 'recharts';
import { ArrowDownLeft, ArrowUpRight } from 'lucide-react';
import { Zap } from "lucide-react";

export default function PerformanceChart({ results }) {
  const [chartType, setChartType] = useState('bar'); // 'bar' or 'scatter'

  // Data for bar chart - keeps original structure
  const barChartData = results.map(result => ({
    name: result.test_name.length > 15 ? result.test_name.substring(0,12) + "..." : result.test_name,
    fullName: result.test_name,
    MySQL: result.mysql_avg_duration,
    PostgreSQL: result.postgres_avg_duration,
    queryType: result.query_type.replace(/_/g, ' '),
    faster: result.faster_db
  }));

  // Data for scatter chart - transforms to show performance relationship
  const scatterData = results.map(result => ({
    name: result.test_name,
    MySQL: result.mysql_avg_duration,
    PostgreSQL: result.postgres_avg_duration,
    faster: result.winner,
    x: result.mysql_avg_duration,   // x-axis is MySQL time
    y: result.postgres_avg_duration, // y-axis is PostgreSQL time
    z: result.difference_percent || 1, // z determines the size of dot - larger = bigger difference
    queryType: result.query_type.replace(/_/g, ' '),
    mysql_count: result.mysql_count,
    postgres_count: result.postgres_count,
    mysql_p95: result.mysql_p95,
    postgres_p95: result.postgres_p95,
    mysql_stddev: result.mysql_stddev,
    postgres_stddev: result.postgres_stddev,
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const originalData = results.find(r => (r.test_name.length > 15 ? r.test_name.substring(0,12) + "..." : r.test_name) === label);
      return (
        <div className="p-4 border shadow-lg rounded-md bg-white opacity-95">
          <p className="text-base font-bold">{originalData ? originalData.test_name : label}</p>
          {originalData && <p className="text-sm text-gray-500 mb-2 capitalize">{originalData.query_type.replace(/_/g, ' ')}</p>}

          <div className="text-xs text-gray-600 mb-2">
            {originalData.mysql_count} runs<br />
            P95: {originalData.mysql_p95.toFixed(2)}s<br />
            σ: {originalData.mysql_stddev.toFixed(2)}s
          </div>

          <div className="flex items-center text-blue-600 mb-1">
            <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
            <span className="font-medium">MySQL:</span>
            <span className="ml-1">{payload[0].value !== null ? payload[0].value.toFixed(3) + ' s' : 'N/A'}</span>
          </div>

          <div className="flex items-center text-green-600 mb-1">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span className="font-medium">PostgreSQL:</span>
            <span className="ml-1">{payload[1].value !== null ? payload[1].value.toFixed(3) + ' s' : 'N/A'}</span>
          </div>

          {originalData && originalData.winner !== 'Tie' && (
            <div className="mt-2 pt-2 border-t text-sm">
              <span className={`font-medium ${originalData.winner === 'MySQL' ? 'text-blue-600' : 'text-green-600'}`}>
                {originalData.winner} is {originalData.difference_percent.toFixed(1)}% faster
              </span>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  const ScatterTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="p-4 border shadow-lg rounded-md bg-white opacity-95">
          <p className="text-base font-bold">{data.name}</p>
          <p className="text-sm text-gray-500 mb-2 capitalize">{data.queryType}</p>

          <div className="flex items-center text-blue-600 mb-1">
            <div className="text-xs text-gray-600 ml-5 mt-0.5">
              {data.postgres_count} runs<br />
              P95: {data.postgres_p95.toFixed(2)}s<br />
              σ: {data.postgres_stddev.toFixed(2)}s
            </div>
            <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
            <span className="font-medium">MySQL:</span>
            <span className="ml-1">{data.MySQL.toFixed(3) + ' s'}</span>
          </div>
          <div className="flex items-center text-green-600 mb-3">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span className="font-medium">PostgreSQL:</span>
            <span className="ml-1">{data.PostgreSQL.toFixed(3) + ' s'}</span>
          </div>

          {data.winner !== 'Tie' && (
            <div className="flex items-center">
              {data.winner === 'MySQL' ?
                <ArrowDownLeft size={16} className="text-blue-600 mr-1" /> :
                <ArrowUpRight size={16} className="text-green-600 mr-1" />
              }
              <span className={`font-medium ${data.winner === 'MySQL' ? 'text-blue-600' : 'text-green-600'}`}>
                {data.winner} is {(data.z).toFixed(1)}% faster
              </span>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card bg-white shadow-xl border-2 border-gray-200">
      <div className="card-body p-6">
        <div className="flex flex-wrap justify-between items-center mb-4">
          <h2 className="card-title text-xl md:text-2xl">Performance Comparison</h2>

          <div className="tabs tabs-boxed">
            <a
              className={`tab ${chartType === 'bar' ? 'tab-active' : ''}`}
              onClick={() => setChartType('bar')}
            >
              Bar Chart
            </a>
            <a
              className={`tab ${chartType === 'scatter' ? 'tab-active' : ''}`}
              onClick={() => setChartType('scatter')}
            >
              Scatter Plot
            </a>
          </div>
        </div>

        <div className="h-96 w-full bg-gradient-to-br from-gray-50 to-white rounded-lg p-4">
          {chartType === 'bar' ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={barChartData}
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
                    value: 'Duration (seconds)',
                    angle: -90,
                    position: 'insideLeft',
                    style: { textAnchor: 'middle', fontSize: 12, fill: '#555' },
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
                  barSize={14}
                  isAnimationActive={true}
                  animationDuration={1500}
                />
                <Bar
                  dataKey="PostgreSQL"
                  fill="#10b981"
                  name="PostgreSQL"
                  radius={[4, 4, 0, 0]}
                  barSize={14}
                  isAnimationActive={true}
                  animationDuration={1500}
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart
                margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis
                  type="number"
                  dataKey="x"
                  name="MySQL Duration"
                  unit=" s"
                  label={{
                    value: 'MySQL Duration (s)',
                    position: 'bottom',
                    style: { textAnchor: 'middle', fontSize: 12, fill: '#3b82f6' },
                    dy: 15
                  }}
                  domain={['auto', 'auto']}
                  tick={{ fontSize: 11, fill: '#444' }}
                />
                <YAxis
                  type="number"
                  dataKey="y"
                  name="PostgreSQL Duration"
                  unit=" s"
                  label={{
                    value: 'PostgreSQL Duration (s)',
                    angle: -90,
                    position: 'left',
                    style: { textAnchor: 'middle', fontSize: 12, fill: '#10b981' },
                    dx: -15
                  }}
                  domain={['auto', 'auto']}
                  tick={{ fontSize: 11, fill: '#444' }}
                />
                <ZAxis type="number" dataKey="z" range={[30, 500]} />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} content={<ScatterTooltip />} />
                <Legend verticalAlign="top" height={36} />

                {/* Equality line (x=y) - where both DBs perform equally */}
                <Scatter name="Equal Performance" data={[
                  { x: 0, y: 0 },
                  { x: Math.max(...scatterData.map(d => Math.max(d.x, d.y))) * 1.1, y: Math.max(...scatterData.map(d => Math.max(d.x, d.y))) * 1.1 }
                ]} line={{ stroke: '#888', strokeWidth: 2, strokeDasharray: '5 5' }} fill="#888" shape="none" />

                <Scatter name="Test Results" data={scatterData} isAnimationActive={true} animationDuration={1500}>
                  {scatterData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.faster === 'MySQL' ? '#3b82f6' : entry.faster === 'PostgreSQL' ? '#10b981' : '#9ca3af'}
                    />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          )}
        </div>

        {chartType === 'scatter' && (
          <div className="mt-4 bg-blue-50 p-3 rounded-md border border-blue-100 text-sm">
            <p className="font-medium text-gray-700">How to read this chart:</p>
            <ul className="text-gray-600 mt-1 list-disc list-inside space-y-1">
              <li>Points <span className="text-blue-600 font-medium">below</span> the diagonal line indicate MySQL is faster</li>
              <li>Points <span className="text-green-600 font-medium">above</span> the diagonal line indicate PostgreSQL is faster</li>
              <li>Larger points indicate a bigger performance difference</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}