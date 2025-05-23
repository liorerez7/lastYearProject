//import React from "react";
//import { Zap, Gauge, Timer, ArrowDown, Award, TrendingDown } from "lucide-react";
//import { AlertCircle } from "lucide-react";
//
//export default function BenchmarkCard({ result }) {
//     const {
//      test_name,
//      mysql_avg_duration,
//      postgres_avg_duration,
//      mysql_p95,
//      postgres_p95,
//      mysql_stddev,
//      postgres_stddev,
//      mysql_count,
//      postgres_count,
//      query_type,
//      winner,
//      difference_percent
//    } = result;
//
//  const faster_db = winner; // התאמה לשם החדש בקוד
//  const performance_gain_percent = difference_percent;
//
//  const formatDuration = (duration) => {
//    if (duration === null || duration === undefined) return "N/A";
//    return duration < 0.001
//      ? `${(duration * 1000000).toFixed(0)} µs`
//      : duration < 1
//      ? `${(duration * 1000).toFixed(1)} ms`
//      : `${duration.toFixed(2)} s`;
//  };
//
//  const getCardStyle = () => {
//    if (faster_db === "MySQL") {
//      return {
//        borderColorClass: "border-blue-400",
//        bgClass: "bg-gradient-to-br from-blue-50 via-white to-blue-100",
//        iconColor: "text-blue-600",
//        badgeClass: "badge-info bg-blue-100 text-blue-700 border-blue-300",
//        dbColor: "text-blue-700",
//      };
//    } else if (faster_db === "PostgreSQL") {
//      return {
//        borderColorClass: "border-green-400",
//        bgClass: "bg-gradient-to-br from-green-50 via-white to-green-100",
//        iconColor: "text-green-600",
//        badgeClass: "badge-success bg-green-100 text-green-700 border-green-300",
//        dbColor: "text-green-700",
//      };
//    } else {
//      return {
//        borderColorClass: "border-gray-300",
//        bgClass: "bg-gradient-to-br from-gray-50 via-white to-gray-100",
//        iconColor: "text-gray-600",
//        badgeClass: "badge-ghost bg-gray-200 text-gray-700 border-gray-400",
//        dbColor: "text-gray-600",
//      };
//    }
//  };
//
//  const hasUnstableData = () => {
//    const lowRuns = mysql_count < 5 || postgres_count < 5;
//    const highVariance = mysql_stddev > mysql_avg_duration || postgres_stddev > postgres_avg_duration;
//    return lowRuns || highVariance;
//  };
//
//  const styles = getCardStyle();
//
//  const getIcon = () => {
//    if (faster_db === "MySQL" || faster_db === "PostgreSQL") {
//      return <Zap size={16} className={styles.iconColor} />;
//    }
//    return <Gauge size={16} className="text-gray-600" />;
//  };
//
//  const getPerformanceIcon = () => {
//    if (faster_db === "MySQL") {
//      return <ArrowDown size={14} className="ml-1 text-blue-600" />;
//    } else if (faster_db === "PostgreSQL") {
//      return <ArrowDown size={14} className="ml-1 text-green-600" />;
//    }
//    return null;
//  };
//
//  const formattedQueryType = query_type
//    ?.replace(/_/g, " ")
//    .replace(/\b\w/g, (l) => l.toUpperCase());
//
//  return (
//    <div
//      className={`card card-compact shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-2 ${styles.borderColorClass} ${styles.bgClass}`}
//    >
//      <div className="card-body p-4">
//        <div className="flex justify-between items-start mb-2">
//          <h2 className="card-title text-base font-semibold leading-tight">
//            {test_name}
//          </h2>
//          <div className="flex items-center gap-2">
//            {faster_db !== "N/A" && (
//              <div
//                className={`badge ${styles.badgeClass} gap-1 text-xs font-semibold`}
//              >
//                {getIcon()}
//                {faster_db}
//              </div>
//            )}
//            {hasUnstableData() && (
//              <div
//                className="tooltip tooltip-left"
//                data-tip="Unstable: low run count or high stddev"
//              >
//                <AlertCircle size={16} className="text-yellow-500" />
//              </div>
//            )}
//          </div>
//        </div>
//
//        <div className="badge badge-outline badge-sm mb-3 capitalize font-medium">
//          <Timer size={12} className="mr-1" />
//          {formattedQueryType}
//        </div>
//
//        <div className="grid grid-cols-2 gap-3 text-center my-2">
//          <div className="bg-white rounded-lg p-2 shadow-sm border border-blue-200">
//            <div className="text-xs font-medium text-blue-600">MySQL</div>
//            <div className="mt-1 text-sm font-bold text-blue-700">
//              {formatDuration(mysql_avg_duration)}
//            </div>
//            <div className="text-[11px] text-gray-500 mt-0.5">
//              {mysql_count} runs<br />
//              P95: {mysql_p95.toFixed(2)}s<br />
//              σ: {mysql_stddev.toFixed(2)}s
//            </div>
//          </div>
//
//          <div className="bg-white rounded-lg p-2 shadow-sm border border-green-200">
//            <div className="text-xs font-medium text-green-600">PostgreSQL</div>
//            <div className="mt-1 text-sm font-bold text-green-700">
//              {formatDuration(postgres_avg_duration)}
//            </div>
//            <div className="text-[11px] text-gray-500 mt-0.5">
//              {postgres_count} runs<br />
//              P95: {postgres_p95.toFixed(2)}s<br />
//              σ: {postgres_stddev.toFixed(2)}s
//            </div>
//          </div>
//        </div>
//
//        {faster_db !== "Tie" && performance_gain_percent > 0 && (
//          <div className="text-xs bg-white p-2 rounded-md border mt-2 shadow-sm text-center relative">
//            <Award size={12} className="inline-block mr-1" />
//            <span className="font-medium">
//              <span className={styles.iconColor}>
//                {performance_gain_percent.toFixed(1)}% faster
//              </span>
//            </span>
//            {getPerformanceIcon()}
//          </div>
//        )}
//
//        {faster_db === "Tie" && (
//          <div className="text-xs bg-gray-50 p-2 rounded-md border mt-2 shadow-sm text-center text-gray-600">
//            <TrendingDown size={12} className="inline-block mr-1" />
//            Performance difference is negligible
//          </div>
//        )}
//      </div>
//    </div>
//  );
//}
import React from "react";
import { Zap, Gauge, Timer, ArrowDown, Award, TrendingDown, Users } from "lucide-react";
import { AlertCircle } from "lucide-react";

export default function BenchmarkCard({ result }) {
  const {
    test_name,
    mysql_avg_duration,
    postgres_avg_duration,
    mysql_p95,
    postgres_p95,
    mysql_stddev,
    postgres_stddev,
    mysql_count,
    postgres_count,
    query_type,
    winner,
    difference_percent
  } = result;

  const faster_db = winner;
  const performance_gain_percent = difference_percent;

  // Extract user count from test_name (e.g., "smoke_10u" -> 10)
  const extractUserCount = (testName) => {
    const match = testName.match(/(\d+)u/);
    return match ? parseInt(match[1]) : null;
  };

  // Generate user-friendly test name
  const generateFriendlyTestName = (testName, queryType) => {
    const userCount = extractUserCount(testName);
    const baseType = testName.replace(/_\d+u$/, '').replace(/_/g, ' ');
    const formattedQueryType = queryType?.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()) || 'Unknown';

    // Create a more descriptive name
    const typeMap = {
      'smoke': 'Performance Test',
      'lookup': 'Data Lookup Test',
      'insert': 'Insert Operation Test',
      'update': 'Update Operation Test',
      'delete': 'Delete Operation Test',
      'complex': 'Complex Query Test'
    };

    const friendlyType = typeMap[baseType.toLowerCase()] || baseType.charAt(0).toUpperCase() + baseType.slice(1) + ' Test';

    return {
      title: friendlyType,
      queryType: formattedQueryType,
      userCount
    };
  };

  const friendlyNames = generateFriendlyTestName(test_name, query_type);

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

  const hasUnstableData = () => {
    const lowRuns = mysql_count < 5 || postgres_count < 5;
    const highVariance = mysql_stddev > mysql_avg_duration || postgres_stddev > postgres_avg_duration;
    return lowRuns || highVariance;
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

  return (
    <div
      className={`card card-compact shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-2 ${styles.borderColorClass} ${styles.bgClass}`}
    >
      <div className="card-body p-5">
        {/* Header with title and winner badge */}
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1">
            <h2 className="card-title text-lg font-bold leading-tight text-gray-800 mb-1">
              {friendlyNames.title}
            </h2>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <div className="badge badge-outline badge-sm capitalize font-medium">
                <Timer size={12} className="mr-1" />
                {friendlyNames.queryType}
              </div>
              {friendlyNames.userCount && (
                <div className="badge badge-outline badge-sm font-medium bg-orange-50 text-orange-700 border-orange-300">
                  <Users size={12} className="mr-1" />
                  {friendlyNames.userCount} Users
                </div>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2 ml-3">
            {faster_db !== "N/A" && (
              <div
                className={`badge ${styles.badgeClass} gap-1 text-xs font-semibold px-3 py-2`}
              >
                {getIcon()}
                {faster_db}
              </div>
            )}
            {hasUnstableData() && (
              <div
                className="tooltip tooltip-left"
                data-tip="Unstable: low run count or high stddev"
              >
                <AlertCircle size={18} className="text-yellow-500" />
              </div>
            )}
          </div>
        </div>

        {/* Performance metrics grid */}
        <div className="grid grid-cols-2 gap-4 text-center my-4">
          <div className="bg-white rounded-xl p-4 shadow-sm border border-blue-200 hover:shadow-md transition-shadow">
            <div className="text-sm font-semibold text-blue-600 mb-2">MySQL</div>
            <div className="text-lg font-bold text-blue-700 mb-2">
              {formatDuration(mysql_avg_duration)}
            </div>
            <div className="text-xs text-gray-500 space-y-1">
              <div>{mysql_count} runs</div>
              <div>P95: {mysql_p95.toFixed(2)}s</div>
              <div>σ: {mysql_stddev.toFixed(2)}s</div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-4 shadow-sm border border-green-200 hover:shadow-md transition-shadow">
            <div className="text-sm font-semibold text-green-600 mb-2">PostgreSQL</div>
            <div className="text-lg font-bold text-green-700 mb-2">
              {formatDuration(postgres_avg_duration)}
            </div>
            <div className="text-xs text-gray-500 space-y-1">
              <div>{postgres_count} runs</div>
              <div>P95: {postgres_p95.toFixed(2)}s</div>
              <div>σ: {postgres_stddev.toFixed(2)}s</div>
            </div>
          </div>
        </div>

        {/* Performance gain indicator */}
        {faster_db !== "Tie" && performance_gain_percent > 0 && (
          <div className="bg-white p-3 rounded-lg border mt-3 shadow-sm text-center relative">
            <div className="flex items-center justify-center">
              <Award size={14} className="mr-2" />
              <span className="font-semibold text-sm">
                <span className={styles.iconColor}>
                  {performance_gain_percent.toFixed(1)}% faster
                </span>
              </span>
              {getPerformanceIcon()}
            </div>
          </div>
        )}

        {faster_db === "Tie" && (
          <div className="bg-gray-50 p-3 rounded-lg border mt-3 shadow-sm text-center text-gray-600">
            <div className="flex items-center justify-center">
              <TrendingDown size={14} className="mr-2" />
              <span className="text-sm font-medium">Performance difference is negligible</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}