import React from 'react';

const SummaryPanel = ({ mysqlWins, postgresWins, totalImprovement, recommendations }) => {
  return (
    <div className="border rounded-lg p-6">
      <h2 className="text-xl font-bold mb-4">סיכום והמלצות</h2>
      <div className="flex justify-between items-center mb-6">
        <div className="text-center">
          <div className="text-3xl font-bold text-blue-600">{mysqlWins}</div>
          <div className="text-sm text-gray-600">MySQL ניצחונות</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-green-600">{postgresWins}</div>
          <div className="text-sm text-gray-600">PostgreSQL ניצחונות</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold">{totalImprovement}%</div>
          <div className="text-sm text-gray-600">הבדל ממוצע</div>
        </div>
      </div>


      <p className="whitespace-pre-line">{recommendations}</p>
    </div>
  );
};

export default SummaryPanel;
