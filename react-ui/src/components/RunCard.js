import React from 'react';
import { useNavigate } from 'react-router-dom';

const RunCard = ({ run }) => {
  const navigate = useNavigate();
  const { id, plan_name, started_at, status } = run;

  const formattedDate = new Date(started_at).toLocaleString();

  const getStatusStyle = () => {
    switch(status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'running': return 'bg-blue-100 text-blue-800';
      case 'finished': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div
      className="border rounded-lg p-4 mb-4 hover:shadow-md cursor-pointer transition-shadow"
      onClick={() => navigate(`/runs/${id}`)}
    >
      <div className="flex justify-between items-center">
        <h3 className="font-semibold text-lg">{plan_name}</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusStyle()}`}>
          {status}
        </span>
      </div>
      <div className="mt-2 text-sm text-gray-600">{formattedDate}</div>
      <div className="mt-3 flex items-center">
        <div className="bg-blue-50 px-3 py-1 rounded mr-2">
          <span className="font-medium text-blue-700">MySQL</span>
        </div>
        <div className="text-gray-400 mx-1">vs</div>
        <div className="bg-green-50 px-3 py-1 rounded">
          <span className="font-medium text-green-700">PostgreSQL</span>
        </div>
      </div>
    </div>
  );
};

export default RunCard;
