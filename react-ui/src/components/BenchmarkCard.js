import React from "react";
import { Zap, Gauge, Timer, ArrowDown, Award, TrendingDown } from "lucide-react";

export default function BenchmarkCard({ result }) {
  const {
    test_name,
    mysql_avg_duration,
    postgres_avg_duration,
    query_type,
    winner,                // ← כמו בקוד הישן
    difference_percent     // ← כמו בקוד הישן
  } = result;

  const faster_db = winner; // התאמה לשם החדש בקוד
  const performance_gain_percent = difference_percent;

  const formatDuration = (duration) => {
    if (duration === null || duration === undefined) return "N/A";
    return duration < 0.001
      ? `${(duration * 1000000).toFixed(0)} µs`
      : duration < 1
      ? `${(duration * 1000).toFixed(1)} ms`
      : `${duration.toFixed(2)} s`;
  };

  const getCardStyle = () => {
    if (faster_db === "MySQL") {
      return {
        borderColorClass: "border-blue-400",
        bgClass: "bg-gradient-to-br from-blue-50 via-white to-blue-100",
        iconColor: "text-blue-600",
        badgeClass: "badge-info bg-blue-100 text-blue-700 border-blue-300",
        dbColor: "text-blue-700",
      };
    } else if (faster_db === "PostgreSQL") {
      return {
        borderColorClass: "border-green-400",
        bgClass: "bg-gradient-to-br from-green-50 via-white to-green-100",
        iconColor: "text-green-600",
        badgeClass: "badge-success bg-green-100 text-green-700 border-green-300",
        dbColor: "text-green-700",
      };
    } else {
      return {
        borderColorClass: "border-gray-300",
        bgClass: "bg-gradient-to-br from-gray-50 via-white to-gray-100",
        iconColor: "text-gray-600",
        badgeClass: "badge-ghost bg-gray-200 text-gray-700 border-gray-400",
        dbColor: "text-gray-600",
      };
    }
  };

  const styles = getCardStyle();

  const getIcon = () => {
    if (faster_db === "MySQL" || faster_db === "PostgreSQL") {
      return <Zap size={16} className={styles.iconColor} />;
    }
    return <Gauge size={16} className="text-gray-600" />;
  };

  const getPerformanceIcon = () => {
    if (faster_db === "MySQL") {
      return <ArrowDown size={14} className="ml-1 text-blue-600" />;
    } else if (faster_db === "PostgreSQL") {
      return <ArrowDown size={14} className="ml-1 text-green-600" />;
    }
    return null;
  };

  const formattedQueryType = query_type
    ?.replace(/_/g, " ")
    .replace(/\b\w/g, (l) => l.toUpperCase());

  return (
    <div
      className={`card card-compact shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-2 ${styles.borderColorClass} ${styles.bgClass}`}
    >
      <div className="card-body p-4">
        <div className="flex justify-between items-start mb-2">
          <h2 className="card-title text-base font-semibold leading-tight">
            {test_name}
          </h2>
          {faster_db !== "N/A" && (
            <div
              className={`badge ${styles.badgeClass} gap-1 text-xs font-semibold`}
            >
              {getIcon()}
              {faster_db}
            </div>
          )}
        </div>

        <div className="badge badge-outline badge-sm mb-3 capitalize font-medium">
          <Timer size={12} className="mr-1" />
          {formattedQueryType}
        </div>

        <div className="grid grid-cols-2 gap-3 text-center my-2">
          <div className="bg-white rounded-lg p-2 shadow-sm border border-blue-200">
            <div className="text-xs font-medium text-blue-600">MySQL</div>
            <div className="mt-1 text-sm font-bold text-blue-700">
              {formatDuration(mysql_avg_duration)}
            </div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow-sm border border-green-200">
            <div className="text-xs font-medium text-green-600">PostgreSQL</div>
            <div className="mt-1 text-sm font-bold text-green-700">
              {formatDuration(postgres_avg_duration)}
            </div>
          </div>
        </div>

        {faster_db !== "Tie" && performance_gain_percent > 0 && (
          <div className="text-xs bg-white p-2 rounded-md border mt-2 shadow-sm text-center relative">
            <Award size={12} className="inline-block mr-1" />
            <span className="font-medium">
              <span className={styles.iconColor}>
                {performance_gain_percent.toFixed(1)}% faster
              </span>
            </span>
            {getPerformanceIcon()}
          </div>
        )}

        {faster_db === "Tie" && (
          <div className="text-xs bg-gray-50 p-2 rounded-md border mt-2 shadow-sm text-center text-gray-600">
            <TrendingDown size={12} className="inline-block mr-1" />
            Performance difference is negligible
          </div>
        )}
      </div>
    </div>
  );
}
