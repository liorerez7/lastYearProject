import React from 'react';
import { CheckCircle, AlertCircle, TrendingUp, ArrowUpRight, Database, Server, Cpu, BarChart2, Zap, BarChartHorizontalBig, HelpCircle, Sparkles, Info as InfoIcon } from "lucide-react"; // Renamed Info to avoid conflict


export default function BenchmarkSummary({ results, rawExecutions }) { // rawExecutions might still be needed for schema if not reliably on results[0]
  if (!results || results.length === 0) {
    return (
      <div className="p-6 text-center text-neutral-500">
        <InfoIcon className="mx-auto h-12 w-12 text-neutral-400 mb-4" />
        No summary data available to display.
      </div>
    );
  }

  // Calculations based on 'winner' and 'difference_percent' from the 'results' prop
  const mysqlWins = results.filter(r => r.winner === 'MySQL').length;
  const postgresWins = results.filter(r => r.winner === 'PostgreSQL').length;
  const ties = results.length - mysqlWins - postgresWins;

  const mysqlTestsWon = results.filter(r => r.winner === 'MySQL');
  const pgTestsWon = results.filter(r => r.winner === 'PostgreSQL');

  const mysqlAvgGain = mysqlTestsWon.length > 0 ?
    mysqlTestsWon.reduce((sum, test) => sum + test.difference_percent, 0) / mysqlTestsWon.length : 0;

  const pgAvgGain = pgTestsWon.length > 0 ?
    pgTestsWon.reduce((sum, test) => sum + test.difference_percent, 0) / pgTestsWon.length : 0;

  const overallWinnerDb = mysqlWins > postgresWins ? 'MySQL' : postgresWins > mysqlWins ? 'PostgreSQL' : 'Tie';

  const strongestMysqlWin = [...mysqlTestsWon].sort((a, b) => b.difference_percent - a.difference_percent)[0];
  const strongestPgWin = [...pgTestsWon].sort((a, b) => b.difference_percent - a.difference_percent)[0];

  // Dynamic strengths from your old code
  const getDynamicStrengths = (dbName) => {
    const strengths = {};
    results.forEach(r => {
      if (r.winner === dbName) {
        // Use a more generic formatting for query_type to category name
        const queryTypeKey = r.query_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        if (!strengths[queryTypeKey]) {
          strengths[queryTypeKey] = { wins: 0, totalDiff: 0, testNames: [] };
        }
        strengths[queryTypeKey].wins += 1;
        strengths[queryTypeKey].totalDiff += r.difference_percent; // Use difference_percent
        strengths[queryTypeKey].testNames.push(r.test_name);
      }
    });

    return Object.entries(strengths)
      .map(([queryType, data]) => ({
        category: queryType,
        // Adapted description
        description: `Won ${data.wins} test(s) in "${queryType}", e.g., ${data.testNames.slice(0,1).join(', ')}${data.testNames.length > 1 ? ' & others' : ''}. Average lead approx. ${(data.totalDiff / data.wins).toFixed(0)}%.` ,
        icon: <BarChart2 size={20} className={dbName === 'MySQL' ? "text-blue-500 mr-2" : "text-green-500 mr-2"} /> // Generic icon, color coded
      }))
      .sort((a,b) => (b.totalDiff / b.wins) - (a.totalDiff / a.wins)) // Sort by impact
      .slice(0, 3); // Show top 3 impactful categories
  };

  const mysqlDynamicStrengths = getDynamicStrengths("MySQL");
  const postgresDynamicStrengths = getDynamicStrengths("PostgreSQL");

  // Overall winner message from your old code
  let overallWinnerMessage = "Overall, MySQL and PostgreSQL showed comparable performance in this test suite.";
  if (overallWinnerDb === "MySQL") {
    overallWinnerMessage = `Overall, MySQL demonstrated stronger performance, winning ${mysqlWins} out of ${results.length} distinct test categories.`;
  } else if (overallWinnerDb === "PostgreSQL") {
    overallWinnerMessage = `Overall, PostgreSQL demonstrated stronger performance, winning ${postgresWins} out of ${results.length} distinct test categories.`;
  }

  // Attempt to get schemaName (as in your old logic)
  const schemaName = results[0]?.schema || (rawExecutions && rawExecutions[0]?.schema) || "<Schema Name>";


  // Static ideal use cases from new code (can be kept as supplementary)
  const idealUseCases = {
    MySQL: [
      "Web application backends",
      "Content management systems",
      "E-commerce platforms",
      "OLTP workloads with simple queries",
      "Applications needing high read/write throughput for simple operations"
    ],
    PostgreSQL: [
      "Data warehousing",
      "Business intelligence applications",
      "Complex analytical workloads (OLAP)",
      "Systems requiring advanced SQL features & data integrity",
      "Applications with geospatial data or complex data types"
    ]
  };


  return (
    <div className="space-y-8">
      {/* Overall statistics cards - Structure from New Code, data from merged logic */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* MySQL Performance Card */}
        <div className="card bg-gradient-to-br from-blue-50 via-white to-blue-100 shadow-xl border-2 border-blue-200">
          <div className="card-body p-5 md:p-6">
            <h2 className="card-title text-blue-700 flex items-center text-lg md:text-xl">
              <Database size={20} className="mr-2 opacity-80" />
              MySQL Performance
            </h2>
            <div className="stats bg-white/70 shadow my-3 text-xs sm:text-sm">
              <div className="stat p-2 sm:p-3">
                <div className="stat-title text-blue-600/80">Tests Won</div>
                <div className="stat-value text-blue-600 text-xl sm:text-2xl">{mysqlWins}</div>
                <div className="stat-desc text-blue-500/70">{results.length > 0 && `${((mysqlWins/results.length)*100).toFixed(0)}% of total`}</div>
              </div>
            </div>
            {mysqlTestsWon.length > 0 && (
              <div className="text-xs sm:text-sm space-y-2">
                <div className="font-semibold flex items-center text-blue-600">
                  <TrendingUp size={16} className="mr-1" />
                  Avg. Lead When Winning: <span className="ml-1 text-blue-700 font-bold">{mysqlAvgGain.toFixed(1)}%</span>
                </div>
                {strongestMysqlWin && (
                  <div className="bg-white p-2.5 rounded-md shadow-sm border border-blue-200">
                    <div className="text-xs text-gray-500">Strongest Advantage In:</div>
                    <div className="font-medium text-blue-700 truncate" title={strongestMysqlWin.test_name}>{strongestMysqlWin.test_name}</div>
                    <div className="text-xs mt-0.5 text-blue-600">
                      {strongestMysqlWin.difference_percent.toFixed(1)}% faster
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* PostgreSQL Performance Card */}
        <div className="card bg-gradient-to-br from-green-50 via-white to-green-100 shadow-xl border-2 border-green-200">
          <div className="card-body p-5 md:p-6">
            <h2 className="card-title text-green-700 flex items-center text-lg md:text-xl">
              <Database size={20} className="mr-2 opacity-80" />
              PostgreSQL Performance
            </h2>
            <div className="stats bg-white/70 shadow my-3 text-xs sm:text-sm">
              <div className="stat p-2 sm:p-3">
                <div className="stat-title text-green-600/80">Tests Won</div>
                <div className="stat-value text-green-600 text-xl sm:text-2xl">{postgresWins}</div>
                <div className="stat-desc text-green-500/70">{results.length > 0 && `${((postgresWins/results.length)*100).toFixed(0)}% of total`}</div>
              </div>
            </div>
            {pgTestsWon.length > 0 && (
              <div className="text-xs sm:text-sm space-y-2">
                <div className="font-semibold flex items-center text-green-600">
                  <TrendingUp size={16} className="mr-1" />
                  Avg. Lead When Winning: <span className="ml-1 text-green-700 font-bold">{pgAvgGain.toFixed(1)}%</span>
                </div>
                {strongestPgWin && (
                  <div className="bg-white p-2.5 rounded-md shadow-sm border border-green-200">
                    <div className="text-xs text-gray-500">Strongest Advantage In:</div>
                    <div className="font-medium text-green-700 truncate" title={strongestPgWin.test_name}>{strongestPgWin.test_name}</div>
                    <div className="text-xs mt-0.5 text-green-600">
                      {strongestPgWin.difference_percent.toFixed(1)}% faster
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Overall Assessment Card (using stats from old code) */}
        <div className="card bg-white shadow-xl border-2 border-gray-200">
          <div className="card-body p-5 md:p-6">
            <h2 className="card-title text-gray-700 flex items-center text-lg md:text-xl">
              <BarChartHorizontalBig size={20} className="mr-2 text-purple-500 opacity-80" />
              Overall Assessment
            </h2>
             <div className="stats bg-gray-50 shadow my-3 text-xs sm:text-sm">
                <div className="stat p-2 sm:p-3">
                    <div className="stat-title text-gray-600/80">Tied Tests</div>
                    <div className="stat-value text-gray-600 text-xl sm:text-2xl">{ties}</div>
                    <div className="stat-desc text-gray-500/70">{results.length > 0 && `${((ties/results.length)*100).toFixed(0)}% of total`}</div>
                </div>
            </div>
            <div className="mt-2 text-sm text-center">
              {overallWinnerDb === 'MySQL' && <p className="font-semibold text-blue-700">MySQL leads overall by {mysqlWins - postgresWins} test categories.</p>}
              {overallWinnerDb === 'PostgreSQL' && <p className="font-semibold text-green-700">PostgreSQL leads overall by {postgresWins - mysqlWins} test categories.</p>}
              {overallWinnerDb === 'Tie' && <p className="font-semibold text-purple-700">Performance is closely matched or tied overall.</p>}
            </div>
          </div>
        </div>
      </div>

      {/* Dynamic Strengths section */}
      <h3 className="text-xl md:text-2xl font-bold mt-10 mb-4 text-center text-neutral-700">Key Performance Areas</h3>
      <div className="grid md:grid-cols-2 gap-6 md:gap-8">
        {/* MySQL Dynamic Strengths */}
        <div className="card bg-gradient-to-br from-blue-50 via-white to-blue-100 shadow-xl border-2 border-blue-200">
          <div className="card-body p-5 md:p-6">
            <h3 className="card-title text-blue-700 flex items-center text-lg md:text-xl">
              <Zap className="mr-2 opacity-80" /> {/* Changed from Database for variety */}
              MySQL Strengths
            </h3>
            <div className="divider mt-1 mb-3"></div>
            {mysqlDynamicStrengths.length > 0 ? (
              <ul className="space-y-3">
                {mysqlDynamicStrengths.map((item, i) => (
                  <li key={`mysql-dyn-strength-${i}`} className="bg-white p-3 rounded-lg shadow-sm border border-blue-100 hover:shadow-md transition-shadow">
                    <div className="flex items-start mb-1">
                      {item.icon} {/* Icon from getDynamicStrengths */}
                      <h4 className="font-semibold text-blue-700 text-sm md:text-base">{item.category}</h4>
                    </div>
                    <p className="text-xs md:text-sm text-gray-600 ml-7">{item.description}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="flex items-center text-neutral-600 italic p-3 bg-blue-50 rounded-lg border border-blue-100 text-sm">
                <InfoIcon className="w-5 h-5 mr-2 text-blue-400 flex-shrink-0" />
                MySQL did not show specific standout advantages in this run based on query categories.
              </div>
            )}
          </div>
        </div>

        {/* PostgreSQL Dynamic Strengths */}
        <div className="card bg-gradient-to-br from-green-50 via-white to-green-100 shadow-xl border-2 border-green-200">
          <div className="card-body p-5 md:p-6">
            <h3 className="card-title text-green-700 flex items-center text-lg md:text-xl">
              <Zap className="mr-2 opacity-80" />
              PostgreSQL Strengths
            </h3>
            <div className="divider mt-1 mb-3"></div>
            {postgresDynamicStrengths.length > 0 ? (
              <ul className="space-y-3">
                {postgresDynamicStrengths.map((item, i) => (
                  <li key={`pg-dyn-strength-${i}`} className="bg-white p-3 rounded-lg shadow-sm border border-green-100 hover:shadow-md transition-shadow">
                    <div className="flex items-start mb-1">
                      {item.icon} {/* Icon from getDynamicStrengths */}
                      <h4 className="font-semibold text-green-700 text-sm md:text-base">{item.category}</h4>
                    </div>
                    <p className="text-xs md:text-sm text-gray-600 ml-7">{item.description}</p>
                  </li>
                ))}
              </ul>
            ) : (
               <div className="flex items-center text-neutral-600 italic p-3 bg-green-50 rounded-lg border border-green-100 text-sm">
                <InfoIcon className="w-5 h-5 mr-2 text-green-400 flex-shrink-0" />
                PostgreSQL did not show specific standout advantages in this run based on query categories.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* General recommendation & Ideal Use Cases */}
      <div className="card bg-white shadow-xl border-t-4 border-purple-500 mt-10">
        <div className="card-body p-5 md:p-6">
          <h3 className="card-title text-xl flex items-center text-purple-700">
            <Sparkles className="mr-2 opacity-80" /> {/* Changed from AlertCircle */}
            Summary & Recommendation
          </h3>
          <div className="divider mt-1 mb-4"></div>

          <div className="bg-gradient-to-r from-purple-50/50 via-indigo-50/50 to-blue-50/50 p-4 md:p-6 rounded-lg border border-purple-100">
            <h4 className="font-semibold text-neutral-700 mb-1">Concluding Remarks for Schema: <code className="bg-base-200 px-1.5 py-0.5 rounded text-sm text-secondary">{schemaName}</code></h4>
            <p className="text-gray-800 leading-relaxed text-sm md:text-base mb-3">{overallWinnerMessage}</p>

            <strong className="block text-sm md:text-base text-neutral-700">Guidance:</strong>
            <p className="text-gray-700 leading-relaxed text-sm mt-1">
                {overallWinnerDb !== "Tie"
                ? `Based on these results, ${overallWinnerDb} appears to be the more performant choice for workloads resembling this benchmark. Review the specific performance areas above where ${overallWinnerDb} excelled.`
                : "Performance was largely comparable. Your choice may depend on other factors such as specific feature requirements, existing team expertise, licensing, or the nature of queries most critical to your application (see 'Key Performance Areas')."
                }
            </p>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* MySQL Ideal Use Cases */}
              <div className="bg-white p-3 md:p-4 rounded-lg shadow-sm border border-blue-100">
                <h4 className="font-bold text-blue-700 flex items-center text-sm md:text-base">
                  <ArrowUpRight size={18} className="mr-1 flex-shrink-0" />
                  MySQL Typically Excels In:
                </h4>
                <ul className="text-xs md:text-sm text-gray-600 mt-2 list-disc list-inside space-y-1 pl-1">
                  {idealUseCases.MySQL.map(useCase => <li key={useCase}>{useCase}</li>)}
                </ul>
              </div>

              {/* PostgreSQL Ideal Use Cases */}
              <div className="bg-white p-3 md:p-4 rounded-lg shadow-sm border border-green-100">
                <h4 className="font-bold text-green-700 flex items-center text-sm md:text-base">
                  <ArrowUpRight size={18} className="mr-1 flex-shrink-0" />
                  PostgreSQL Typically Excels In:
                </h4>
                <ul className="text-xs md:text-sm text-gray-600 mt-2 list-disc list-inside space-y-1 pl-1">
                  {idealUseCases.PostgreSQL.map(useCase => <li key={useCase}>{useCase}</li>)}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
      <p className="text-xs text-neutral-500 mt-6 text-center">
            Disclaimer: Benchmark results are indicative and can vary based on specific queries, data distribution, hardware configurations, and software versions. Always test with your own workload.
      </p>
    </div>
  );
}