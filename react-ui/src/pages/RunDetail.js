import React from "react";
import { Clock, Calendar, Database, Cloud, Play, CheckCircle, XCircle, AlertCircle, Eye } from "lucide-react";
import { useParams } from "react-router-dom";
import { useQuery } from "react-query";
import { getRun } from "../api/runs_api";

const RunDetail = () => {
  const { id } = useParams();

  const {
  data: run,
  isLoading,
  isError,
  refetch,
} = useQuery(["run", id], () => getRun(id), {
  refetchInterval: (data) => {
    if (!data) return 3000; // עדיין לא נטען
    return data.status === "done" || data.status === "completed" ? false : 3000;
  },
  refetchIntervalInBackground: true
});


  if (isLoading) {
    return <div className="p-6 text-center text-neutral-500">Loading run details...</div>;
  }

  if (isError || !run) {
    return <div className="p-6 text-center text-red-500">Failed to load run data.</div>;
  }

  const formatDate = (dateString) => {
    if (!dateString) return "—";
    const date = new Date(dateString);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  };

  const calculateDuration = (start, end) => {
    if (!start || !end) return "—";
    const startTime = new Date(start);
    const endTime = new Date(end);
    const diffMs = endTime - startTime;
    const minutes = Math.floor(diffMs / 60000);
    const seconds = Math.floor((diffMs % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  };

  const getStatusConfig = (status) => {
    switch (status?.toLowerCase()) {
      case "done":
      case "completed":
        return {
          color: "text-emerald-700",
          bg: "bg-emerald-50",
          border: "border-emerald-200",
          icon: CheckCircle,
          label: "Completed"
        };
      case "pending":
        return {
          color: "text-amber-700",
          bg: "bg-amber-50",
          border: "border-amber-200",
          icon: AlertCircle,
          label: "Pending"
        };
      case "running":
        return {
          color: "text-blue-700",
          bg: "bg-blue-50",
          border: "border-blue-200",
          icon: Play,
          label: "Running"
        };
      case "failed":
        return {
          color: "text-red-700",
          bg: "bg-red-50",
          border: "border-red-200",
          icon: XCircle,
          label: "Failed"
        };
      default:
        return {
          color: "text-gray-700",
          bg: "bg-gray-50",
          border: "border-gray-200",
          icon: AlertCircle,
          label: "Unknown"
        };
    }
  };

  const getDatabaseIcon = (db) => {
    const colors = {
      mysql: "text-orange-600 bg-orange-100",
      postgres: "text-blue-600 bg-blue-100",
      postgresql: "text-blue-600 bg-blue-100",
      mongodb: "text-green-600 bg-green-100",
    };
    return colors[db?.toLowerCase()] || "text-gray-600 bg-gray-100";
  };

  const getCloudIcon = (provider) => {
    const colors = {
      aws: "text-orange-500 bg-orange-100",
      azure: "text-blue-500 bg-blue-100",
      gcp: "text-green-500 bg-green-100",
      google: "text-green-500 bg-green-100",
    };
    return colors[provider?.toLowerCase()] || "text-gray-500 bg-gray-100";
  };

  const statusConfig = getStatusConfig(run.status);
  const StatusIcon = statusConfig.icon;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="h-8 w-1 bg-blue-600 rounded-full"></div>
            <h1 className="text-3xl font-bold text-gray-900">Test Details</h1>
          </div>
          <p className="text-gray-600 ml-5">Comprehensive view of your test execution</p>
        </div>

        {/* Compact Test Card */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-xl transition-all duration-300">
          {/* Compact Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold">{run.plan_name}</h2>
                <p className="text-blue-100 text-xs">ID: {run.id}</p>
              </div>
              <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border ${statusConfig.border} ${statusConfig.bg} ${statusConfig.color} font-medium text-sm`}>
                <StatusIcon className="h-3.5 w-3.5" />
                <span>{statusConfig.label}</span>
              </div>
            </div>
          </div>

          <div className="p-6">
            {/* Compact Stats - 2 rows, 4 columns */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {/* Duration */}
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-purple-100 text-purple-600">
                  <Clock className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium">Duration</p>
                  <p className="text-sm font-bold text-gray-900">
                    {calculateDuration(run.started_at, run.finished_at)}
                  </p>
                </div>
              </div>

              {/* Cloud */}
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${getCloudIcon(run.cloud_provider)}`}>
                  <Cloud className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium">Cloud</p>
                  <p className="text-sm font-bold text-gray-900 capitalize">{run.cloud_provider}</p>
                </div>
              </div>

              {/* Started */}
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-green-100 text-green-600">
                  <Calendar className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium">Started</p>
                  <p className="text-xs font-bold text-gray-900">{formatDate(run.started_at)}</p>
                </div>
              </div>

              {/* Completed */}
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-red-100 text-red-600">
                  <Calendar className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium">Completed</p>
                  <p className="text-xs font-bold text-gray-900">{formatDate(run.finished_at)}</p>
                </div>
              </div>
            </div>

            {/* Compact Database Migration */}
            <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg p-4 mb-4 border border-gray-100">
              <div className="flex items-center justify-between">
                {/* Source DB */}
                <div className="flex items-center gap-2">
                  <div className={`p-2 rounded-lg ${getDatabaseIcon(run.source_db)}`}>
                    <Database className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 font-medium">From</p>
                    <p className="text-sm font-bold text-gray-900 capitalize">{run.source_db}</p>
                  </div>
                </div>

                {/* Arrow */}
                <div className="bg-blue-600 text-white rounded-full p-2">
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </div>

                {/* Destination DB */}
                <div className="flex items-center gap-2">
                  <div className={`p-2 rounded-lg ${getDatabaseIcon(run.destination_db)}`}>
                    <Database className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 font-medium">To</p>
                    <p className="text-sm font-bold text-gray-900 capitalize">{run.destination_db}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Button */}
            <button
              disabled={run.status !== "done" && run.status !== "completed"}
              className={`w-full font-semibold py-3 px-4 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 shadow-md
                ${run.status === "done" || run.status === "completed"
                  ? "bg-blue-600 hover:bg-blue-700 text-white"
                  : "bg-gray-300 text-gray-500 cursor-not-allowed"}`}
              onClick={() => {
                if (run.status === "done" || run.status === "completed") {
                  window.location.href = `/executions/${run.id}`;
                }
              }}
            >
              <Eye className="h-4 w-4" />
              View Execution Results
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RunDetail;
