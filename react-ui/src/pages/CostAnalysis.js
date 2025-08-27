import React, { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, BarChartBig, Users } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

// Color palette for clear differentiation
const MYSQL_COLOR = "#0ea5e9"; // sky-500 (MySQL)
const PG_COLOR = "#8b5cf6"; // violet-500 (Postgres)

// --- Performance dataset to reflect in the visuals ---
const DEMO_RESULTS = [
  // (your DEMO_RESULTS data here, unchanged) ...
  // Keeping as-is to avoid flooding, but same as what you had before
];

// --- Helpers ---
function parseSelected(test_id) {
  return DEMO_RESULTS.find((r) => r.test_name === test_id);
}

// Fake CloudWatch-like metrics
function fakeFetchCloudWatch(test_id) {
  const selected = parseSelected(test_id);
  return new Promise((resolve) => {
    setTimeout(() => {
      const timestamps = Array.from({ length: 8 }, (_, i) => `T+${i * 5}m`);
      const baseLoad = selected ? selected.load_level : 25;
      const winner = selected?.winner || "MySQL";

      const data = timestamps.map((t, i) => {
        const pulse = 1 + 0.06 * Math.sin(i / 1.5);
        const loadFactor = 0.8 + baseLoad / 50;

        const mysqlBias = winner === "MySQL" ? 0.9 : 1.05;
        const pgBias = winner === "PostgreSQL" ? 0.9 : 1.05;

        const mysqlCPU = Math.max(
          15,
          (28 + Math.random() * 12) * pulse * loadFactor * mysqlBias
        );
        const pgCPU = Math.max(
          15,
          (28 + Math.random() * 12) * pulse * loadFactor * pgBias
        );

        const mysqlIOPS = Math.max(
          400,
          (650 + Math.random() * 300) * pulse * loadFactor * mysqlBias
        );
        const pgIOPS = Math.max(
          400,
          (650 + Math.random() * 300) * pulse * loadFactor * pgBias
        );

        return {
          time: t,
          mysqlCPU: +mysqlCPU.toFixed(1),
          pgCPU: +pgCPU.toFixed(1),
          mysqlIOPS: Math.round(mysqlIOPS),
          pgIOPS: Math.round(pgIOPS),
        };
      });

      resolve(data);
    }, 400);
  });
}

// Build workloads
const fakeWorkloads = DEMO_RESULTS.map((r) => {
  const requests = Math.max(r.mysql_count, r.postgres_count) * 100;
  const secs =
    (requests * Math.min(r.mysql_avg_duration, r.postgres_avg_duration)) / 2;
  const durationMin = Math.max(8, secs / 60);
  return {
    test: r.test_name,
    users: r.load_level,
    requests,
    durationMin: +durationMin.toFixed(0),
    query_type: r.query_type,
    winner: r.winner,
    mysql_avg_duration: r.mysql_avg_duration,
    postgres_avg_duration: r.postgres_avg_duration,
  };
});

// Fake costs
function fakeFetchCosts(test_id, metrics) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const INSTANCE_RATE_MYSQL = 0.25;
      const INSTANCE_RATE_PG = 0.28;
      const PER_CPU_POINT = 0.002;
      const PER_KIOPS = 0.00008;
      const PER_REQ_SEC_MYSQL = 0.00002;
      const PER_REQ_SEC_PG = 0.000022;

      const workloads = fakeWorkloads.map((w) => {
        const hrs = w.durationMin / 60;
        const mysqlReqCost =
          w.requests * w.mysql_avg_duration * PER_REQ_SEC_MYSQL;
        const pgReqCost =
          w.requests * w.postgres_avg_duration * PER_REQ_SEC_PG;
        const mysqlCost = INSTANCE_RATE_MYSQL * hrs + mysqlReqCost;
        const pgCost = INSTANCE_RATE_PG * hrs + pgReqCost;
        return {
          ...w,
          mysqlCost: +mysqlCost.toFixed(2),
          pgCost: +pgCost.toFixed(2),
          mysqlPer1000: +(
            mysqlCost /
            (w.requests / 1000)
          ).toFixed(4),
          pgPer1000: +(
            pgCost /
            (w.requests / 1000)
          ).toFixed(4),
          cheaper:
            mysqlCost < pgCost
              ? "MySQL"
              : pgCost < mysqlCost
              ? "PostgreSQL"
              : "Tie",
        };
      });

      const timeline = metrics.map((m) => {
        const minutes = 5;
        const mysqlCost =
          (INSTANCE_RATE_MYSQL / 60) * minutes +
          (m.mysqlCPU * PER_CPU_POINT / 60) * minutes +
          ((m.mysqlIOPS / 1000) * PER_KIOPS) * minutes;
        const pgCost =
          (INSTANCE_RATE_PG / 60) * minutes +
          (m.pgCPU * PER_CPU_POINT / 60) * minutes +
          ((m.pgIOPS / 1000) * PER_KIOPS) * minutes;
        return {
          time: m.time,
          mysqlCost: +mysqlCost.toFixed(3),
          pgCost: +pgCost.toFixed(3),
        };
      });

      resolve({ workloads, timeline });
    }, 350);
  });
}

export default function CostAnalysis() {
  const { test_id } = useParams();
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState([]);
  const [costs, setCosts] = useState({ workloads: [], timeline: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function loadData() {
      setLoading(true);
      const m = await fakeFetchCloudWatch(test_id);
      if (!mounted) return;
      setMetrics(m);
      const c = await fakeFetchCosts(test_id, m);
      if (!mounted) return;
      setCosts(c);
      setLoading(false);
    }
    loadData();
    return () => {
      mounted = false;
    };
  }, [test_id]);

  const selectedRow = useMemo(() => parseSelected(test_id), [test_id]);

  const filteredWorkloads = useMemo(() => {
    if (!selectedRow) return costs.workloads;
    const sameType = costs.workloads.filter(
      (w) => w.query_type === selectedRow.query_type
    );
    const others = costs.workloads.filter(
      (w) => w.query_type !== selectedRow.query_type
    );
    return [...sameType, ...others];
  }, [costs.workloads, selectedRow]);

  const overall = useMemo(() => {
    const mysql = costs.timeline.reduce((s, p) => s + (p.mysqlCost || 0), 0);
    const pg = costs.timeline.reduce((s, p) => s + (p.pgCost || 0), 0);
    const cheaper = mysql < pg ? "MySQL" : pg < mysql ? "PostgreSQL" : "Tie";
    const diff = Math.abs(mysql - pg);
    const percent =
      Math.max(mysql, pg) > 0 ? (diff / Math.max(mysql, pg)) * 100 : 0;
    return {
      mysql: +mysql.toFixed(2),
      pg: +pg.toFixed(2),
      cheaper,
      diff: +diff.toFixed(2),
      percent: +percent.toFixed(1),
    };
  }, [costs.timeline]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen text-center">
        <div className="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-12 w-12 mb-4 border-t-primary"></div>
        <h2 className="text-xl font-semibold text-primary">
          Fetching CloudWatch & Cost Data...
        </h2>
        <p className="text-neutral-500">
          Simulating analysis for Test ID: {test_id}
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-indigo-50 to-emerald-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="bg-white rounded-xl shadow-lg border-t-4 border-amber-400 p-6 mb-6">
          <h1 className="text-2xl md:text-3xl font-bold text-amber-700 flex items-center gap-2">
            <BarChartBig size={28} className="text-amber-600" />
            Cost Analysis Dashboard
          </h1>
          <p className="text-sm text-neutral-600 mt-1">
            Test ID:{" "}
            <code className="bg-base-200 px-1.5 py-0.5 rounded">{test_id}</code>
          </p>
          {selectedRow && (
            <p className="text-xs text-neutral-600 mt-1">
              Query: <strong>{selectedRow.query_type}</strong>, Load:{" "}
              <strong>{selectedRow.load_level} users</strong>, Winner by perf:{" "}
              <strong>{selectedRow.winner}</strong>
            </p>
          )}
          <p className="text-xs text-neutral-500 mt-2">
            ⚠️ Data is <strong>fabricated</strong> from DEMO_RESULTS +
            CloudWatch-like signals & demo cost model.
          </p>
          <div className="mt-4">
            <button
              onClick={() => navigate(-1)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 bg-white hover:bg-gray-50 text-sm"
            >
              <ArrowLeft size={16} /> Back
            </button>
          </div>
        </header>

        {/* CPU Chart */}
        <div className="bg-white rounded-xl shadow-md border p-6 mb-6">
          <h2 className="text-lg font-bold mb-4 text-gray-700">
            CPU Utilization (%)
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="mysqlCPU"
                stroke={MYSQL_COLOR}
                name="MySQL CPU"
              />
              <Line
                type="monotone"
                dataKey="pgCPU"
                stroke={PG_COLOR}
                name="Postgres CPU"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* IOPS Chart */}
        <div className="bg-white rounded-xl shadow-md border p-6 mb-6">
          <h2 className="text-lg font-bold mb-4 text-gray-700">IOPS</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="mysqlIOPS"
                stroke={MYSQL_COLOR}
                name="MySQL IOPS"
              />
              <Line
                type="monotone"
                dataKey="pgIOPS"
                stroke={PG_COLOR}
                name="Postgres IOPS"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Cost Timeline */}
        <div className="bg-white rounded-xl shadow-md border p-6 mb-6">
          <h2 className="text-lg font-bold mb-4 text-gray-700">
            Estimated Cost Over Time ($)
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={costs.timeline}>
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar
                dataKey="mysqlCost"
                fill={MYSQL_COLOR}
                name="MySQL Cost"
              />
              <Bar
                dataKey="pgCost"
                fill={PG_COLOR}
                name="Postgres Cost"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Overall Cost Verdict & Recommendation */}
        <div className="bg-white rounded-xl shadow-md border p-6 text-center">
          <h2 className="text-lg font-bold mb-3 text-gray-800">
            Overall Cost Verdict
          </h2>

          <div className="grid md:grid-cols-3 gap-4 mb-4">
            <div className="p-4 rounded-lg border bg-amber-50">
              <div className="text-xs text-neutral-600">Total — MySQL</div>
              <div className="text-2xl font-bold text-amber-600">
                ${overall.mysql}
              </div>
            </div>
            <div className="p-4 rounded-lg border bg-indigo-50">
              <div className="text-xs text-neutral-600">Total — PostgreSQL</div>
              <div className="text-2xl font-bold text-indigo-600">
                ${overall.pg}
              </div>
            </div>
            <div className="p-4 rounded-lg border bg-emerald-50">
              <div className="text-xs text-neutral-600">Cheaper Overall</div>
              <div className="text-2xl font-bold text-emerald-700">
                {overall.cheaper}
                {overall.cheaper !== "Tie"
                  ? ` (-$${overall.diff}, ${overall.percent}% less)`
                  : ""}
              </div>
            </div>
          </div>

          <p className="text-sm md:text-base text-neutral-800 leading-relaxed">
            Based on the full run, the cheaper engine is{" "}
            <strong>{overall.cheaper}</strong>.
            <br className="hidden md:block" />
            <span className="inline-block mt-1">
              🚀 <strong>Recommendation:</strong> run the database on{" "}
              <strong>AWS PostgreSQL</strong> (Amazon RDS for PostgreSQL /
              Aurora PostgreSQL) for a great balance of cost, features, and
              ecosystem.
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
