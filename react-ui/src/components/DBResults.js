import React from 'react';
import ResultItem from './ResultItem';

const DBResults = ({ dbName, execution }) => {
  console.log("Execution object received for DB:", dbName, execution);

  return (
    <div className="db-panel">
      <h3>{dbName}</h3>
      {execution ? (
        <>
          <p><b>Test ID:</b> {execution.test_id}</p>
          <p><b>SK:</b> {execution.SK}</p>
          <p><b>DB Type:</b> {execution.dbType}</p>
          <p><b>Test Type:</b> {execution.testType}</p>
          <p><b>Schema:</b> {execution.schema}</p>
          <p><b>Timestamp:</b> {execution.timestamp}</p>

          <div className="query-scroll">
            <h4>Queries:</h4>
            {Array.isArray(execution.queries) && execution.queries.length > 0 ? (
              execution.queries.map((query, index) => (
                <ResultItem key={index} result={query} />
              ))
            ) : (
              <p>No queries available</p>
            )}
          </div>
        </>
      ) : (
        <>
          <p>No data</p>
          <p>No queries</p>
        </>
      )}
    </div>
  );
};

export default DBResults;
