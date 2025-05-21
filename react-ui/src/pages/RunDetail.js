import React from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "react-query";
import { getRun } from "../api/runs_api";

const RunDetail = () => {
  const { id } = useParams();
  const { data: run, isLoading, isError } = useQuery(["run", id], () => getRun(id));

  if (isLoading)
    return <div className="flex justify-center items-center h-64">טוען…</div>;
  if (isError)
    return <div className="text-red-600 p-4">שגיאה בטעינת נתונים</div>;

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">פרטי הרצה</h1>

      <div className="bg-white rounded shadow p-4 space-y-4">
        <div>
          <span className="font-semibold">Plan Name:</span>{" "}
          {run.plan_name}
        </div>

        <div>
          <span className="font-semibold">Start Time:</span>{" "}
          {new Date(run.started_at).toLocaleString()}
        </div>

        <div>
          <span className="font-semibold">End Time:</span>{" "}
          {run.finished_at ? new Date(run.finished_at).toLocaleString() : "—"}
        </div>

        <div>
          <span className="font-semibold">Cloud Provider:</span>{" "}
          {run.cloud_provider}
        </div>

        <div>
          <span className="font-semibold">Source DB:</span>{" "}
          {run.source_db}
        </div>

        <div>
          <span className="font-semibold">Destination DB:</span>{" "}
          {run.destination_db}
        </div>

        <div>
          <span className="font-semibold">Status:</span>{" "}
          {run.status}
        </div>

        <div className="pt-4">
          <button
            className="text-blue-600 hover:underline"
            onClick={() => window.location.href = `/executions/${run.id}`}
          >
            ▶ הצג תוצאות (לא פעיל כרגע)
          </button>
        </div>
      </div>
    </div>
  );
};

export default RunDetail;
