import React, { useState } from 'react';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runMigration = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("http://localhost:8000/run-migration", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: "mysql",
          destination: "postgres"
        })
      });

      const data = await response.json();

      if (!response.ok) {
        console.error("Migration API Error:", data);
        throw new Error(data.detail || "Something went wrong");
      }

      setResult(data);
    } catch (err) {
      console.error("Frontend Error:", err);
      setError(err.message || "Unknown error occurred");
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>Database Migration UI</h1>
      <button onClick={runMigration} disabled={loading}>
        {loading ? "Running..." : "Run Migration"}
      </button>

      {error && (
        <p style={{ color: "red", marginTop: "1rem" }}>❌ {error}</p>
      )}

      {result && (
        <div style={{ marginTop: "1rem" }}>
          <h3>✅ Migration Complete</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
