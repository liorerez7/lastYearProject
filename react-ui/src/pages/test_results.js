import React from 'react';
import { useLocation } from 'react-router-dom';
import DBResults from '../components/DBResults';
import './test_results.css';

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

  const mysql = testData.test_id?.execution?.mysql;
  const postgres = testData.test_id?.execution?.postgres;
  console.log("mysql", mysql);
  console.log("postgres", postgres);

  return (
    <div className="test-result-container">
      <h1>✅ Test Created Successfully!</h1>


      <h2>Execution:</h2>
      <div className="db-columns">
        <DBResults dbName="mysql" execution={mysql} />
        <DBResults dbName="postgres" execution={postgres} />
      </div>
    </div>
  );
}
