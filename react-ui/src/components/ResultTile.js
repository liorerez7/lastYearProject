import React from 'react';

const ResultTile = ({ title, subtitle, mysqlTime, postgresTime, winner }) => {
  const diff = mysqlTime && postgresTime ?
    ((Math.max(mysqlTime, postgresTime) - Math.min(mysqlTime, postgresTime)) /
    Math.max(mysqlTime, postgresTime) * 100).toFixed(1) : 0;

  const getWinnerStyle = () => {
    if (winner === 'mysql') return 'bg-blue-50';
    if (winner === 'postgres') return 'bg-green-50';
    return 'bg-gray-50';
  };

  return (
    <div className={`border rounded-lg p-4 mb-4 ${getWinnerStyle()}`}>
      <div className="flex justify-between items-center">
        <div>
          <h3 className="font-semibold text-lg">{title}</h3>
          {subtitle && <div className="text-xs text-gray-500">{subtitle}</div>}
        </div>
        {winner && (
          <div className={`text-xs font-medium ${winner === 'mysql' ? 'text-blue-700' : 'text-green-700'}`}>
            {winner === 'mysql' ? 'MySQL מהיר יותר ב-' : 'PostgreSQL מהיר יותר ב-'}{diff}%
          </div>
        )}
      </div>
      <div className="flex justify-between mt-3">
        <div>
          <div className="text-sm text-gray-600">MySQL</div>
          <div className={`text-lg font-semibold ${winner === 'mysql' ? 'text-blue-700' : ''}`}>
            {mysqlTime} s
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-600 text-right">PostgreSQL</div>
          <div className={`text-lg font-semibold text-right ${winner === 'postgres' ? 'text-green-700' : ''}`}>
            {postgresTime} s
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultTile;
