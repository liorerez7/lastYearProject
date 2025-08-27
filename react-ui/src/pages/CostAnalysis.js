
// --------------------------------------------------------------------------------------------------------------------------------------------
import React, { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, BarChartBig } from "lucide-react";
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

// Color palette
const MYSQL_COLOR = "#0ea5e9"; // sky-500 (MySQL)
const PG_COLOR = "#8b5cf6"; // violet-500 (Postgres)

// ----------------------- Utilities -----------------------
function clamp(v, min, max) {
  return Math.min(max, Math.max(min, v));
}

// ----------------------- Synthetic series -----------------------
function generateSyntheticMetrics() {
  // 12 points: T+0m, T+5m, ..., T+55m
  const N = 12;
  const timestamps = Array.from({ length: N }, (_, i) => `T+${i * 5}m`);
  const twoPi = Math.PI * 2;

  // Helper small ripples for “less static” look
  const ripple = (t) =>
    0.6 * Math.sin(twoPi * 2.2 * t) + 0.4 * Math.cos(twoPi * 3.1 * t);
  const ripple2 = (t) =>
    0.5 * Math.sin(twoPi * 1.3 * t) + 0.3 * Math.cos(twoPi * 2.7 * t);

  const out = [];
  for (let i = 0; i < N; i++) {
    const t = i / (N - 1); // normalize to [0,1]

    // Peaks: sharp mid (PURE COUNT) + milder late (PAGINATION)
    const g1 = Math.exp(-Math.pow(t - 0.45, 2) / (2 * Math.pow(0.09, 2))); // sharp mid
    const g2 = Math.exp(-Math.pow(t - 0.78, 2) / (2 * Math.pow(0.12, 2))); // late bump

    // ---------------- CPU ----------------
    // PG — slightly higher baseline, with gentle but visible volatility
    let pgCPU_raw =
      58.5 +
      3.0 * t +
      1.2 * Math.sin(twoPi * 0.9 * t) +
      0.8 * Math.cos(twoPi * 1.4 * t) +
      0.5 * ripple(t);

    // MySQL — under PG most of the time, with events above PG
    const myBase =
      (58.5 + 3.0 * t) - 8.5 - 0.7 * t + 0.4 * ripple2(t); // base below PG
    let myCPU_raw = myBase + 26 * g1 + 10 * g2 + 0.6 * ripple(t); // more contrast + wavy

    // ---------------- IOPS ----------------
    // Tie IOPS to CPU & events, keep PG steadier but correlated
    let pgIO_raw =
      1180 + 7.5 * pgCPU_raw + 25 * t + 12 * ripple2(t) + 40 * g1; // mild rise near PURE COUNT
    let myIO_raw =
      980 + 9.5 * myCPU_raw + 18 * ripple(t) + 60 * g1 + 100 * g2; // stronger correlation + events

    // Clamp before overrides
    let mysqlCPU = clamp(myCPU_raw, 5, 98);
    let pgCPU = clamp(pgCPU_raw, 5, 98);
    let mysqlIOPS = clamp(myIO_raw, 200, 6000);
    let pgIOPS = clamp(pgIO_raw, 200, 6000);

    out.push({
      time: timestamps[i],
      mysqlCPU: +mysqlCPU.toFixed(1),
      pgCPU: +pgCPU.toFixed(1),
      mysqlIOPS: Math.round(mysqlIOPS),
      pgIOPS: Math.round(pgIOPS),
    });
  }

  // ---------------- Explicit point overrides as requested ----------------
  // ---------------- Explicit point overrides (CPU + IOPS) ----------------
    const idx25 = 5; // T+25m
    const idx35 = 7; // T+35m
    const idx40 = 8; // T+40m
    const idx45 = 9; // T+45m

    // T+25m: PURE COUNT — MySQL IOPS ≈ 2000, PG מראה עומס קל (CPU~64)
    if (out[idx25]) {
      out[idx25].pgCPU = 64.0;                // עומס קל ב-PG לפי הבקשה
      out[idx25].mysqlIOPS = 2000;            // שיא ל-MySQL
      // השארת PG IOPS כפי שמחושב; מינימום קטן כדי להבטיח עלייה עדינה אם צריך
      out[idx25].pgIOPS = Math.round(Math.max(out[idx25].pgIOPS, 1650));
    }

    // T+35m: חזרה לבייסליין — CPU~50% ו-IOPS~1350 ל-MySQL
    if (out[idx35]) {
      out[idx35].mysqlCPU = 50.0;
      out[idx35].mysqlIOPS = 1350;
    }

    // T+40m: PAGINATION — MySQL CPU~66% ו-IOPS~1780
    if (out[idx40]) {
      out[idx40].mysqlCPU = 66.0;
      out[idx40].mysqlIOPS = 1780;
    }

    // T+45m: חזרה לבייסליין — MySQL IOPS~1350
    if (out[idx45]) {
      out[idx45].mysqlIOPS = 1350;
    }


  return out;
}

// Fetch synthetic metrics (no external deps)
function fakeFetchCloudWatch(_ignored_test_id) {
  return Promise.resolve(generateSyntheticMetrics());
}

// Fully synthetic cost model (tilts slightly in favor of MySQL overall)
function fakeFetchCosts(_ignored_test_id, metrics) {
  const WINDOW_MINUTES = 5;

  // Unit costs — emphasize differences + slight advantage to MySQL
  const CPU_UNIT_COST_MY = 0.00105;
  const CPU_UNIT_COST_PG = 0.00140;
  const IO_UNIT_COST_MY = 0.000013;
  const IO_UNIT_COST_PG = 0.000016;
  const BASE_MY = 0.0018; // base per-window
  const BASE_PG = 0.0024;

  const timeline = metrics.map((m) => {
    const my =
      BASE_MY +
      CPU_UNIT_COST_MY * (m.mysqlCPU || 0) +
      IO_UNIT_COST_MY * (m.mysqlIOPS || 0);
    const pg =
      BASE_PG +
      CPU_UNIT_COST_PG * (m.pgCPU || 0) +
      IO_UNIT_COST_PG * (m.pgIOPS || 0);

    return {
      time: m.time,
      mysqlCost: +my.toFixed(4),
      pgCost: +pg.toFixed(4),
      windowMinutes: WINDOW_MINUTES,
    };
  });

  return Promise.resolve({ workloads: [], timeline });
}

// ----------------------- Component -----------------------
export default function CostAnalysis() {
  const { test_id } = useParams();
  const currentTestId = test_id || "synthetic";
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState([]);
  const [costs, setCosts] = useState({ workloads: [], timeline: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    async function loadData() {
      setLoading(true);
      try {
        const m = await fakeFetchCloudWatch(currentTestId);
        if (!mounted) return;
        setMetrics(m);

        const c = await fakeFetchCosts(currentTestId, m);
        if (!mounted) return;
        setCosts(c);
      } catch (error) {
        console.error("Error loading data:", error);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    loadData();
    return () => {
      mounted = false;
    };
  }, [currentTestId]);

  const overall = useMemo(() => {
    const mysql = costs.timeline.reduce((s, p) => s + (p.mysqlCost || 0), 0);
    const pg = costs.timeline.reduce((s, p) => s + (p.pgCost || 0), 0);
    const cheaper = mysql < pg ? "MySQL" : pg < mysql ? "PostgreSQL" : "Tie";
    const diff = Math.abs(mysql - pg);
    const percent = Math.max(mysql, pg) > 0 ? (diff / Math.max(mysql, pg)) * 100 : 0;
    const total = mysql + pg || 1;
    const myShare = (mysql / total) * 100;
    const pgShare = (pg / total) * 100;
    return {
      mysql: +mysql.toFixed(4),
      pg: +pg.toFixed(4),
      cheaper,
      diff: +diff.toFixed(4),
      percent: +percent.toFixed(1),
      myShare: +myShare.toFixed(1),
      pgShare: +pgShare.toFixed(1),
    };
  }, [costs.timeline]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen text-center bg-gradient-to-br from-amber-50 via-indigo-50 to-emerald-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600 mb-4"></div>
        <h2 className="text-xl font-semibold text-amber-700 mb-2">Generating synthetic metrics...</h2>
        <p className="text-neutral-600">
          Test ID: <code className="bg-white px-2 py-1 rounded text-sm">{currentTestId}</code>
        </p>
      </div>
    );
  }

  const isMyWinner = overall.cheaper === "MySQL";
  const isPgWinner = overall.cheaper === "PostgreSQL";

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-indigo-50 to-emerald-50 p-4 md:p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <header className="bg-white rounded-xl shadow-lg border-t-4 border-amber-400 p-6">
          <div className="flex items-center gap-3 mb-3">
            <BarChartBig size={28} className="text-amber-600" />
            <h1 className="text-2xl md:text-3xl font-bold text-amber-700">Cost Analysis Dashboard (Synthetic)</h1>
          </div>

          <div className="space-y-1 mb-4">
            <p className="text-sm text-neutral-600">
              Test ID: <code className="bg-gray-100 px-2 py-1 rounded text-xs">{currentTestId}</code>
            </p>
          </div>

          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 bg-white hover:bg-gray-50 text-sm transition-colors"
          >
            <ArrowLeft size={16} /> Back
          </button>
        </header>

        {/* CPU Utilization Chart */}
        <div className="bg-white rounded-xl shadow-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-700 flex items-center gap-2">CPU Utilization (%)</h2>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="time" tick={{ fontSize: 12 }} axisLine={{ stroke: "#e0e0e0" }} />
              <YAxis tick={{ fontSize: 12 }} axisLine={{ stroke: "#e0e0e0" }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#fff",
                  border: "1px solid #ddd",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="mysqlCPU"
                stroke={MYSQL_COLOR}
                name="MySQL CPU"
                strokeWidth={3}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="pgCPU"
                stroke={PG_COLOR}
                name="PostgreSQL CPU"
                strokeWidth={3}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* IOPS Chart */}
        <div className="bg-white rounded-xl shadow-lg border p-6">
          <h2 className="text-lg font-bold mb-4 text-gray-700">IOPS Performance</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="time" tick={{ fontSize: 12 }} axisLine={{ stroke: "#e0e0e0" }} />
              <YAxis tick={{ fontSize: 12 }} axisLine={{ stroke: "#e0e0e0" }} domain={[0, "auto"]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#fff",
                    border: "1px solid #ddd",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="mysqlIOPS"
                stroke={MYSQL_COLOR}
                name="MySQL IOPS"
                strokeWidth={3}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="pgIOPS"
                stroke={PG_COLOR}
                name="PostgreSQL IOPS"
                strokeWidth={3}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Cost Timeline Chart */}
        <div className="bg-white rounded-xl shadow-lg border p-6">
          <h2 className="text-lg font-bold mb-2 text-gray-700">Cost Timeline ($/5min window)</h2>
          <ResponsiveContainer width="100%" height={340}>
            <BarChart
              data={costs.timeline}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              barCategoryGap="25%"
              barGap={6}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="time" tick={{ fontSize: 11 }} axisLine={{ stroke: "#e0e0e0" }} />
              <YAxis
                domain={[0, "auto"]}
                tickFormatter={(v) => `$${(v ?? 0).toFixed(4)}`}
                tick={{ fontSize: 11 }}
                axisLine={{ stroke: "#e0e0e0" }}
                allowDecimals
              />
              <Tooltip
                formatter={(value, name) => [
                  `$${(+value).toFixed(4)}`,
                  name === "mysqlCost" ? "MySQL" : "PostgreSQL",
                ]}
                labelFormatter={(label) => `Window ${label} (5min)`}
                contentStyle={{
                  backgroundColor: "#fff",
                  border: "1px solid #ddd",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                }}
              />
              <Legend />
              <Bar dataKey="mysqlCost" fill={MYSQL_COLOR} name="MySQL ($/5min)" radius={[3, 3, 0, 0]} />
              <Bar dataKey="pgCost" fill={PG_COLOR} name="PostgreSQL ($/5min)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Cost Summary */}
        <div className="bg-white rounded-xl shadow-lg border p-6">
          <h2 className="text-xl font-bold mb-6 text-gray-800 text-center">💰 Overall Cost Analysis</h2>

          {/* Highlighted totals with visual emphasis */}
          <div className="grid md:grid-cols-3 gap-6 mb-6">
            <div
              className={
                "p-6 rounded-xl border-2 bg-sky-50 " +
                (isMyWinner ? "border-sky-400 ring-2 ring-sky-200" : "border-sky-200")
              }
            >
              <div className="flex items-center justify-between">
                <div className="text-xs font-medium text-sky-700 uppercase tracking-wide">MySQL Total Cost</div>
                {isMyWinner && (
                  <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 border border-emerald-200">
                    Winner
                  </span>
                )}
              </div>
              <div className="text-4xl font-extrabold text-sky-700 mt-1 mb-2">${overall.mysql}</div>
              <div className="text-xs text-sky-700">Share: {overall.myShare}%</div>
            </div>

            <div
              className={
                "p-6 rounded-xl border-2 bg-violet-50 " +
                (isPgWinner ? "border-violet-400 ring-2 ring-violet-200" : "border-violet-200")
              }
            >
              <div className="flex items-center justify-between">
                <div className="text-xs font-medium text-violet-700 uppercase tracking-wide">PostgreSQL Total Cost</div>
                {isPgWinner && (
                  <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 border border-emerald-200">
                    Winner
                  </span>
                )}
              </div>
              <div className="text-4xl font-extrabold text-violet-700 mt-1 mb-2">${overall.pg}</div>
              <div className="text-xs text-violet-700">Share: {overall.pgShare}%</div>
            </div>

            <div className="p-6 rounded-xl border-2 border-emerald-200 bg-emerald-50">
              <div className="text-xs font-medium text-emerald-700 uppercase tracking-wide mb-1">Result</div>
              <div className="text-2xl font-bold text-emerald-800 mb-1">{overall.cheaper}</div>
              {overall.cheaper !== "Tie" && (
                <div className="text-sm text-emerald-700">
                  Saves <span className="font-semibold">${overall.diff}</span> ({overall.percent}%)
                </div>
              )}
            </div>
          </div>



          {/* Explanation */}
          <div className="space-y-3">
            {/* Keep the assumptions section (t3.micro etc.) */}
            <div className="text-xs text-gray-600 space-y-1">
              <p className="font-semibold">Pricing Assumptions:</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>MySQL RDS: <code>$0.018/hour</code> (t3.micro)</li>
                <li>PostgreSQL RDS: <code>$0.020/hour</code> (t3.micro)</li>
                <li>Storage: <code>$0.115/GB/month</code> (GP2)</li>
                <li>Performance impact derived from CPU &amp; IOPS</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
