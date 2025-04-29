import React from 'react';

const ResultItem = ({ result }) => {
  return (
    <div className="query-block">
      <p><b>Query:</b> <code>{result.query}</code></p>
      <p><b>Query Type:</b> {result.query_type}</p>
      <p><b>Repeat:</b> {result.repeat}</p>
      <p><b>Selector:</b> {result.selector}</p>
    </div>
  );
};

export default ResultItem;
