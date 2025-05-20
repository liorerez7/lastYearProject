import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';

export const BarChartComponent = ({ data }) => {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="mysql" fill="#3b82f6" name="MySQL" />
          <Bar dataKey="postgres" fill="#10b981" name="PostgreSQL" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export const RadarChartComponent = ({ data }) => {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid />
          <PolarAngleAxis dataKey="category" />
          <PolarRadiusAxis angle={90} domain={[0, 5]} />
          <Radar name="MySQL" dataKey="mysql" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
          <Radar name="PostgreSQL" dataKey="postgres" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};
