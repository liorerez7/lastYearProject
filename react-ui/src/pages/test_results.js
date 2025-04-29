import React from 'react';
import { useLocation } from 'react-router-dom';

export default function TestResult() {
  const location = useLocation();
  const { testData } = location.state || {};

  if (!testData) {
    return (
      <div style={{ padding: "2rem" }}>
        <h2>❗ No test data found</h2>
        <p>Please create a simple test first.</p>
      </div>
    );
  }

  const executionData = testData.execution || {};

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>✅ Test Created Successfully!</h1>

      <h2>🧾 Metadata:</h2>
      <p><strong>Test ID:</strong> {testData.test_id?.test_id || "N/A"}</p>
      <p><strong>Info:</strong> {testData.metadata}</p>

      <h2>🧪 Query Results:</h2>
      {Object.entries(executionData).map(([dbType, execution]) => (
        <div key={dbType} style={{ marginBottom: "2rem" }}>
          <h3>📌 {dbType.toUpperCase()}</h3>
          <p><strong>Schema:</strong> {execution.schema}</p>
          <p><strong>Timestamp:</strong> {execution.timestamp}</p>

          {execution.queries?.map((q, idx) => (
            <div
              key={idx}
              style={{
                background: "#f6f8fa",
                padding: "1rem",
                borderRadius: "8px",
                marginTop: "1rem",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
              }}
            >
              <div><strong>Query Type:</strong> {q.query_type}</div>
              <div><strong>Repeat:</strong> {q.repeat}</div>
              <div><strong>Selector:</strong> {q.selector}</div>
              <div><strong>Query:</strong></div>
              <pre style={{ whiteSpace: "pre-wrap" }}>{q.query}</pre>
              <div><strong>Durations:</strong> {q.durations?.join(", ")}</div>
              <div><strong>Std Dev:</strong> {q.stddev}</div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
