import React from 'react';
import { useLocation } from 'react-router-dom';

export default function TestResult() {
  const location = useLocation();
  const { testData } = location.state || {}; // Get passed data

  if (!testData) {
    return (
      <div style={{ padding: "2rem" }}>
        <h2>❗ No test data found</h2>
        <p>Please create a simple test first.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>✅ Test Created Successfully!</h1>
      <h2>Test ID:</h2>
      <p>{testData.test_id}</p>

      <h2>Full Server Response:</h2>
      <pre>{JSON.stringify(testData, null, 2)}</pre>
    </div>
  );
}
