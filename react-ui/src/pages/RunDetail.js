import React from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "react-query";
import { getRun } from "../api/runs_api";
import ResultTile from "../components/ResultTile";
import { BarChartComponent, RadarChartComponent } from "../components/PerformanceChart";
import SummaryPanel from "../components/SummaryPanel";

const RunDetail = () => {
  const { id } = useParams();
  const { data: run, isLoading, isError } = useQuery(["run", id], () => getRun(id));

  if (isLoading)
    return <div className="flex justify-center items-center h-64">טוען…</div>;
  if (isError)
    return <div className="text-red-600 p-4">שגיאה בטעינת נתונים</div>;

  const barData = run.results.map(r => ({
    name: r.name,
    mysql: r.mysql_time,
    postgres: r.postgres_time
  }));

  const radarData = Object.entries(run.category_results).map(
    ([cat, v]) => ({
      category: cat,
      mysql: v.mysql_wins,
      postgres: v.postgres_wins
    })
  );

  const mysqlWins = run.results.filter(r => r.winner === "mysql").length;
  const postgresWins = run.results.filter(r => r.winner === "postgres").length;
  const totalImprovement = ((run.results.reduce((s, r) =>
    s + Math.abs(r.mysql_time - r.postgres_time) / Math.max(r.mysql_time, r.postgres_time), 0
  ) / run.results.length) * 100).toFixed(1);

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">
        {run.plan_name} <span className="text-gray-500 text-base font-normal">
        ({new Date(run.started_at).toLocaleString()})</span>
      </h1>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="border rounded-lg p-4">
          <h2 className="font-semibold mb-4 text-right">Bar Chart</h2>
          <BarChartComponent data={barData}/>
        </div>
        <div className="border rounded-lg p-4">
          <h2 className="font-semibold mb-4 text-right">Radar Chart</h2>
          <RadarChartComponent data={radarData}/>
        </div>
      </div>

      <SummaryPanel
        mysqlWins={mysqlWins}
        postgresWins={postgresWins}
        totalImprovement={totalImprovement}
        recommendations={run.recommendations}
      />

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
        {run.results.map(r => (
          <ResultTile key={r.id}
            title={r.name}
            subtitle={r.description}
            mysqlTime={r.mysql_time}
            postgresTime={r.postgres_time}
            winner={r.winner}
          />
        ))}
      </div>
    </div>
  );
};
export default RunDetail;
