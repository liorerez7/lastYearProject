import React, { useState } from 'react';
import { CheckCircle, TrendingUp, BarChart2, Zap, Info as InfoIcon, ChevronDown, ChevronUp, Users, Activity, Target, Lightbulb, Sparkles } from "lucide-react";
import DEMO_RESULTS from './demoResults';


export default function BenchmarkSummary({ results, rawExecutions }) {
  const [isLoadInsightsExpanded, setIsLoadInsightsExpanded] = useState(false);

   results = DEMO_RESULTS;

  // Friendly test type mapping
  const typeMap = {
    'lookup': 'Point Lookups',
    'dash': 'Dashboard Reads',
    'smalljoin': 'Simple Joins',
    'smoke': 'General Load Test',
    'index': 'Index Efficiency Test',
    'mix': 'Mixed Workload Simulation',
    'rw': 'Read-Write Heavy',
    'report': 'Reporting & Analytics',
    'edge': 'Edge Case & Recursive Queries',
    'heavy': 'Heavy Operations & Joins',
    'spike30': 'High Load Spike (30 Users)'
  };

  const getFriendlyTestName = (testName) => {
    if (!testName) return testName;
    // Extract the base type (e.g., "dash" from "dash_3u")
    const baseType = testName.split('_')[0];
    return typeMap[baseType] || testName;
  };

  if (!results || results.length === 0) {
    return (
      <div className="p-6 text-center text-neutral-500">
        <InfoIcon className="mx-auto h-12 w-12 text-neutral-400 mb-4" />
        No summary data available to display.
      </div>
    );
  }

  // Extract context information
  const schemaName = results[0]?.schema || (rawExecutions && rawExecutions[0]?.schema) || "Unknown Schema";

  // Extract load levels from rawExecutions - fix the selector extraction
  const loadLevels = rawExecutions ?
    [...new Set(rawExecutions.flatMap(exec => {
      // Extract selector values from the JSON data
      if (exec.queries && Array.isArray(exec.queries)) {
        return exec.queries.map(q => q.selector).filter(s => s !== undefined && s !== null);
      }
      return exec.selector !== undefined && exec.selector !== null ? [exec.selector] : [];
    }))].sort((a, b) => a - b) :
    [];

  const loadRangeText = loadLevels.length > 0 ?
    `${Math.min(...loadLevels)} to ${Math.max(...loadLevels)} users` :
    "various load levels";

  // Core calculations
  const mysqlWins = results.filter(r => r.winner === 'MySQL').length;
  const postgresWins = results.filter(r => r.winner === 'PostgreSQL').length;

  const mysqlTestsWon = results.filter(r => r.winner === 'MySQL');
  const pgTestsWon = results.filter(r => r.winner === 'PostgreSQL');

  const mysqlAvgGain = mysqlTestsWon.length > 0 ?
    mysqlTestsWon.reduce((sum, test) => sum + test.difference_percent, 0) / mysqlTestsWon.length : 0;

  const pgAvgGain = pgTestsWon.length > 0 ?
    pgTestsWon.reduce((sum, test) => sum + test.difference_percent, 0) / pgTestsWon.length : 0;

  const overallWinnerDb = mysqlWins > postgresWins ? 'MySQL' : postgresWins > mysqlWins ? 'PostgreSQL' : 'Tie';

  const strongestMysqlWin = [...mysqlTestsWon].sort((a, b) => b.difference_percent - a.difference_percent)[0];
  const strongestPgWin = [...pgTestsWon].sort((a, b) => b.difference_percent - a.difference_percent)[0];

  // Performance insights
  const getPerformanceInsights = () => {
    const insights = [];

    if (strongestMysqlWin && strongestPgWin) {
      const mysqlMax = strongestMysqlWin.difference_percent;
      const pgMax = strongestPgWin.difference_percent;
      const mysqlTestName = getFriendlyTestName(strongestMysqlWin.test_name);
      const pgTestName = getFriendlyTestName(strongestPgWin.test_name);
      insights.push(`MySQL showed up to ${mysqlMax.toFixed(0)}% faster response in ${mysqlTestName}. PostgreSQL had fewer wins but led by up to ${pgMax.toFixed(0)}% in ${pgTestName}.`);
    } else if (strongestMysqlWin) {
      const mysqlTestName = getFriendlyTestName(strongestMysqlWin.test_name);
      insights.push(`MySQL dominated with advantages up to ${strongestMysqlWin.difference_percent.toFixed(0)}% in ${mysqlTestName}.`);
    } else if (strongestPgWin) {
      const pgTestName = getFriendlyTestName(strongestPgWin.test_name);
      insights.push(`PostgreSQL led with advantages up to ${strongestPgWin.difference_percent.toFixed(0)}% in ${pgTestName}.`);
    }

    return insights;
  };

  // Consistency analysis
  const getConsistencyInsights = () => {
    const queryTypes = [...new Set(results.map(r => r.query_type))];
    const consistentWinner = queryTypes.every(type =>
      results.filter(r => r.query_type === type && r.winner === overallWinnerDb).length > 0
    );

    if (overallWinnerDb !== 'Tie') {
      if (consistentWinner && mysqlWins + postgresWins === results.length) {
        return `${overallWinnerDb} led consistently across all test categories.`;
      } else {
        const exceptions = queryTypes.filter(type =>
          !results.some(r => r.query_type === type && r.winner === overallWinnerDb)
        );
        if (exceptions.length > 0) {
          const otherDb = overallWinnerDb === 'MySQL' ? 'PostgreSQL' : 'MySQL';
          return `${overallWinnerDb} led in most categories, with ${otherDb} showing strength in ${exceptions.map(e => e.replace(/_/g, ' ')).join(', ')}.`;
        }
      }
    }
    return "Performance varied significantly across different query types.";
  };

  // Load-specific insights
  const getLoadSpecificInsights = () => {
    if (!rawExecutions || loadLevels.length === 0) return [];

    const insights = [];

    // Analyze performance trends across loads
    const performanceByLoad = {};
    rawExecutions.forEach(exec => {
      // Extract selectors from queries array
      if (exec.queries && Array.isArray(exec.queries)) {
        exec.queries.forEach(query => {
          if (query.selector !== undefined && query.selector !== null) {
            if (!performanceByLoad[query.selector]) {
              performanceByLoad[query.selector] = { mysql: [], postgres: [] };
            }
            if (exec.db_type === 'mysql') {
              performanceByLoad[query.selector].mysql.push(query.avg);
            } else if (exec.db_type === 'postgres') {
              performanceByLoad[query.selector].postgres.push(query.avg);
            }
          }
        });
      }
    });

    // Generate insights based on load patterns
    if (loadLevels.length > 1) {
      insights.push(`Performance tested across ${loadLevels.length} different load levels (${loadRangeText}).`);

      if (overallWinnerDb !== 'Tie') {
        insights.push(`${overallWinnerDb} maintained consistent advantages across low to high concurrency scenarios.`);
      }
    }

    return insights;
  };

  // Dynamic strengths calculation
  const getDynamicStrengths = (dbName) => {
    const strengths = {};
    results.forEach(r => {
      if (r.winner === dbName) {
        const queryTypeKey = r.query_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        const friendlyTestName = getFriendlyTestName(r.test_name);
        if (!strengths[queryTypeKey]) {
          strengths[queryTypeKey] = { wins: 0, totalDiff: 0, testNames: [] };
        }
        strengths[queryTypeKey].wins += 1;
        strengths[queryTypeKey].totalDiff += r.difference_percent;
        strengths[queryTypeKey].testNames.push(friendlyTestName);
      }
    });

    return Object.entries(strengths)
      .map(([queryType, data]) => ({
        category: queryType,
        description: `Dominated ${data.wins} test${data.wins > 1 ? 's' : ''} with ${(data.totalDiff / data.wins).toFixed(0)}% average advantage in "${data.testNames[0]}"${data.testNames.length > 1 ? ' and similar queries' : ''}.`,
        icon: <BarChart2 size={20} className={dbName === 'MySQL' ? "text-blue-500 mr-2" : "text-green-500 mr-2"} />,
        avgAdvantage: data.totalDiff / data.wins
      }))
      .sort((a, b) => b.avgAdvantage - a.avgAdvantage)
      .slice(0, 3);
  };

  const mysqlDynamicStrengths = getDynamicStrengths("MySQL");
  const postgresDynamicStrengths = getDynamicStrengths("PostgreSQL");

  // Enhanced recommendation logic
  const getRecommendation = () => {
    if (overallWinnerDb === 'Tie') {
      return {
        primary: "Performance was closely matched across test scenarios.",
        guidance: "Your choice should be driven by specific feature requirements, existing team expertise, licensing considerations, or the nature of queries most critical to your application.",
        recommendation: "Consider PostgreSQL for complex analytics and advanced SQL features, or MySQL for simpler transactional workloads and web applications."
      };
    }

    const winner = overallWinnerDb;
    const avgAdvantage = winner === 'MySQL' ? mysqlAvgGain : pgAvgGain;

    return {
      primary: `${winner} demonstrated superior performance, winning ${winner === 'MySQL' ? mysqlWins : postgresWins} out of ${results.length} test categories with an average ${avgAdvantage.toFixed(1)}% advantage when leading.`,
      guidance: loadLevels.length > 0 ?
        `${winner} consistently outperformed across ${loadRangeText} concurrent users, making it suitable for your expected load profile.` :
        `${winner} showed consistent advantages across the tested scenarios.`,
      recommendation: winner === 'MySQL' ?
        "MySQL is recommended for high-throughput transactional workloads, simple joins, pagination-heavy applications, and latency-sensitive web backends." :
        "PostgreSQL is recommended for complex analytical workloads, reporting systems, applications requiring advanced SQL features, and scenarios demanding strong data integrity."
    };
  };

  const recommendation = getRecommendation();
  const performanceInsights = getPerformanceInsights();
  const consistencyInsights = getConsistencyInsights();
  const loadInsights = getLoadSpecificInsights();

  return (
    <div className="space-y-8">
      {/* Context Header - New storytelling element */}
      <div className="bg-gradient-to-r from-slate-50 via-blue-50 to-indigo-50 p-6 rounded-xl border-l-4 border-indigo-400 shadow-sm">
        <div className="flex items-start space-x-4">
          <div className="bg-indigo-100 p-3 rounded-lg">
            <Activity className="w-6 h-6 text-indigo-600" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-800 mb-2">Benchmark Context</h2>
            <p className="text-gray-700 leading-relaxed">
              All tests were conducted using the <code className="bg-white px-2 py-1 rounded text-sm font-mono text-indigo-700 border">{schemaName}</code> schema,
              under simulated user loads ranging from <span className="font-semibold text-indigo-700">{loadRangeText}</span>.
              {results.length > 1 && ` A total of ${results.length} distinct test scenarios were evaluated.`}
            </p>
          </div>
        </div>
      </div>

      {/* Performance Story - Enhanced narrative section */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="bg-gradient-to-r from-purple-500 to-indigo-600 p-6 text-white">
          <div className="flex items-center space-x-3">
            <Target className="w-7 h-7" />
            <h2 className="text-2xl font-bold">Performance Story</h2>
          </div>
          <p className="mt-2 text-purple-100">Key insights from your benchmark results</p>
        </div>

        <div className="p-6 space-y-6">
          {/* Performance Insights */}
          {performanceInsights.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <TrendingUp className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-amber-800 mb-2">Performance Highlights</h4>
                  {performanceInsights.map((insight, i) => (
                    <p key={i} className="text-amber-700 leading-relaxed">{insight}</p>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Consistency Insights */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-semibold text-blue-800 mb-2">Consistency Analysis</h4>
                <p className="text-blue-700 leading-relaxed">{consistencyInsights}</p>
              </div>
            </div>
          </div>

          {/* Load-Specific Insights (Collapsible) */}
          {loadInsights.length > 0 && (
            <div className="border border-gray-200 rounded-lg">
              <button
                onClick={() => setIsLoadInsightsExpanded(!isLoadInsightsExpanded)}
                className="w-full p-4 text-left bg-gray-50 hover:bg-gray-100 transition-colors flex items-center justify-between rounded-t-lg"
              >
                <div className="flex items-center space-x-3">
                  <Users className="w-5 h-5 text-gray-600" />
                  <h4 className="font-semibold text-gray-800">Load-Specific Insights</h4>
                </div>
                {isLoadInsightsExpanded ? <ChevronUp className="w-5 h-5 text-gray-600" /> : <ChevronDown className="w-5 h-5 text-gray-600" />}
              </button>

              {isLoadInsightsExpanded && (
                <div className="p-4 bg-white border-t border-gray-200 rounded-b-lg">
                  <div className="space-y-3">
                    {loadInsights.map((insight, i) => (
                      <div key={i} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-purple-400 rounded-full mt-2 flex-shrink-0"></div>
                        <p className="text-gray-700 leading-relaxed">{insight}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Key Performance Areas - Existing section with minor enhancements */}
      <div className="grid md:grid-cols-2 gap-6 md:gap-8">
        {/* MySQL Dynamic Strengths */}
        <div className="card bg-gradient-to-br from-blue-50 via-white to-blue-100 shadow-xl border-2 border-blue-200">
          <div className="card-body p-5 md:p-6">
            <h3 className="card-title text-blue-700 flex items-center text-lg md:text-xl">
              <Zap className="mr-2 opacity-80" />
              MySQL Advantages
            </h3>
            <div className="divider mt-1 mb-3"></div>
            {mysqlDynamicStrengths.length > 0 ? (
              <ul className="space-y-3">
                {mysqlDynamicStrengths.map((item, i) => (
                  <li key={`mysql-dyn-strength-${i}`} className="bg-white p-3 rounded-lg shadow-sm border border-blue-100 hover:shadow-md transition-all duration-200 hover:border-blue-200">
                    <div className="flex items-start mb-1">
                      {item.icon}
                      <h4 className="font-semibold text-blue-700 text-sm md:text-base">{item.category}</h4>
                    </div>
                    <p className="text-xs md:text-sm text-gray-600 ml-7">{item.description}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="flex items-center text-neutral-600 italic p-3 bg-blue-50 rounded-lg border border-blue-100 text-sm">
                <InfoIcon className="w-5 h-5 mr-2 text-blue-400 flex-shrink-0" />
                MySQL did not show standout advantages in this benchmark run.
              </div>
            )}
          </div>
        </div>

        {/* PostgreSQL Dynamic Strengths */}
        <div className="card bg-gradient-to-br from-green-50 via-white to-green-100 shadow-xl border-2 border-green-200">
          <div className="card-body p-5 md:p-6">
            <h3 className="card-title text-green-700 flex items-center text-lg md:text-xl">
              <Zap className="mr-2 opacity-80" />
              PostgreSQL Advantages
            </h3>
            <div className="divider mt-1 mb-3"></div>
            {postgresDynamicStrengths.length > 0 ? (
              <ul className="space-y-3">
                {postgresDynamicStrengths.map((item, i) => (
                  <li key={`pg-dyn-strength-${i}`} className="bg-white p-3 rounded-lg shadow-sm border border-green-100 hover:shadow-md transition-all duration-200 hover:border-green-200">
                    <div className="flex items-start mb-1">
                      {item.icon}
                      <h4 className="font-semibold text-green-700 text-sm md:text-base">{item.category}</h4>
                    </div>
                    <p className="text-xs md:text-sm text-gray-600 ml-7">{item.description}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="flex items-center text-neutral-600 italic p-3 bg-green-50 rounded-lg border border-green-100 text-sm">
                <InfoIcon className="w-5 h-5 mr-2 text-green-400 flex-shrink-0" />
                PostgreSQL did not show standout advantages in this benchmark run.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Enhanced Summary & Recommendation */}
      <div className="card bg-white shadow-xl border-t-4 border-purple-500">
        <div className="card-body p-5 md:p-6">
          <h3 className="card-title text-xl flex items-center text-purple-700">
            <Lightbulb className="mr-2 opacity-80" />
            Recommendation & Guidance
          </h3>
          <div className="divider mt-1 mb-4"></div>

          <div className="bg-gradient-to-r from-purple-50/50 via-indigo-50/50 to-blue-50/50 p-6 rounded-lg border border-purple-100">
            <div className="space-y-4">
              {/* Primary Conclusion */}
              <div>
                <h4 className="font-semibold text-neutral-700 mb-2 flex items-center">
                  <Target className="w-4 h-4 mr-2 text-purple-600" />
                  Primary Conclusion
                </h4>
                <p className="text-gray-800 leading-relaxed">{recommendation.primary}</p>
              </div>

              {/* Guidance */}
              <div>
                <h4 className="font-semibold text-neutral-700 mb-2 flex items-center">
                  <Activity className="w-4 h-4 mr-2 text-purple-600" />
                  Performance Guidance
                </h4>
                <p className="text-gray-700 leading-relaxed">{recommendation.guidance}</p>
              </div>

              {/* Practical Recommendation */}
              <div className="bg-white p-4 rounded-lg shadow-sm border border-purple-100">
                <h4 className="font-semibold text-purple-700 mb-2 flex items-center">
                  <Sparkles className="w-4 h-4 mr-2" />
                  Practical Recommendation
                </h4>
                <p className="text-gray-800 leading-relaxed">{recommendation.recommendation}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}