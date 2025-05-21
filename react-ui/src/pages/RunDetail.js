import React from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "react-query";
import { getRun } from "../api/runs_api";

const RunDetail = () => {
  const { id } = useParams();
  const { data: run, isLoading, isError } = useQuery(["run", id], () => getRun(id));

  // Function to format date in a more compact way
  const formatDate = (dateString) => {
    if (!dateString) return "—";
    const date = new Date(dateString);
    return date.toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Function to calculate duration between start and end times
  const calculateDuration = (start, end) => {
    if (!start || !end) return "—";

    const startTime = new Date(start);
    const endTime = new Date(end);
    const diffMs = endTime - startTime;

    const minutes = Math.floor(diffMs / 60000);
    const seconds = Math.floor((diffMs % 60000) / 1000);

    return `${minutes}m ${seconds}s`;
  };

  // Function to determine status badge styling
  const getStatusBadgeClasses = (status) => {
    switch (status?.toLowerCase()) {
      case "done":
        return "bg-green-100 text-green-800 border border-green-200";
      case "pending":
        return "bg-yellow-100 text-yellow-800 border border-yellow-200";
      case "failed":
        return "bg-red-100 text-red-800 border border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border border-gray-200";
    }
  };

  // Function to get status icon
  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case "done":
        return "✓"; // Checkmark
      case "pending":
        return "⏳"; // Hourglass
      case "failed":
        return "✕"; // X mark
      default:
        return "•"; // Bullet point
    }
  };

  if (isLoading)
    return <div className="flex justify-center items-center h-64">טוען…</div>;
  if (isError)
    return <div className="text-red-600 p-4 text-center">שגיאה בטעינת נתונים</div>;

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-6">
      <h1 className="text-2xl font-bold mb-6 text-center">My Tests</h1>

      <div className="space-y-4">
        {/* Test Run Card */}
        <div className="bg-white rounded-lg shadow-md p-5 transition-all duration-300 hover:shadow-lg border border-gray-100">
          {/* Header with Plan Name and Status Badge */}
          <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between">
            <h2 className="text-xl font-semibold text-gray-900">{run.plan_name}</h2>
            <div className="flex items-center mt-2 md:mt-0">
              <span className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1 ${getStatusBadgeClasses(run.status)}`}>
                <span>{getStatusIcon(run.status)}</span>
                <span>{run.status}</span>
              </span>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6 mb-6">
            {/* Left Column */}
            <div className="space-y-5 md:pr-4">
              <div className="flex flex-col">
                <p className="uppercase tracking-wide text-xs text-gray-500 mb-1">Cloud Provider</p>
                <div className="flex items-center">
                  <span className="w-2 h-2 rounded-full bg-blue-500 mr-2"></span>
                  <p className="text-sm text-gray-700 font-medium">{run.cloud_provider}</p>
                </div>
              </div>

              <div className="flex flex-col">
                <p className="uppercase tracking-wide text-xs text-gray-500 mb-1">Source Database</p>
                <div className="flex items-center">
                  <span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span>
                  <p className="text-sm text-gray-700 font-medium">{run.source_db}</p>
                </div>
              </div>

              <div className="flex flex-col">
                <p className="uppercase tracking-wide text-xs text-gray-500 mb-1">Destination Database</p>
                <div className="flex items-center">
                  <span className="w-2 h-2 rounded-full bg-purple-500 mr-2"></span>
                  <p className="text-sm text-gray-700 font-medium">{run.destination_db}</p>
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-5 md:border-l md:border-gray-100 md:pl-4">
              <div className="flex flex-col">
                <p className="uppercase tracking-wide text-xs text-gray-500 mb-1">Start Time</p>
                <div className="flex items-center">
                  <svg className="w-3 h-3 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <p className="text-sm text-gray-700 font-medium">{formatDate(run.started_at)}</p>
                </div>
              </div>

              <div className="flex flex-col">
                <p className="uppercase tracking-wide text-xs text-gray-500 mb-1">End Time</p>
                <div className="flex items-center">
                  <svg className="w-3 h-3 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  <p className="text-sm text-gray-700 font-medium">{formatDate(run.finished_at)}</p>
                </div>
              </div>

              <div className="flex flex-col">
                <p className="uppercase tracking-wide text-xs text-gray-500 mb-1">Duration</p>
                <div className="flex items-center">
                  <svg className="w-3 h-3 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <p className="text-sm text-gray-700 font-medium">{calculateDuration(run.started_at, run.finished_at)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Button */}
          <div className="flex justify-end mt-6 border-t pt-4 border-gray-100">
            <button
              className="flex items-center gap-2 bg-blue-50 text-blue-600 hover:bg-blue-100 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200"
              onClick={() => window.location.href = `/executions/${run.id}`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
              </svg>
              View Execution Results
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RunDetail;