import React, { useState } from 'react';
import { runMigration } from '../api/migration_api';

export default function RunMigrationButton() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleClick = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await runMigration();
      setResult(data);
    } catch (err) {
      setError(err.message || "Unknown error occurred");
    }

    setLoading(false);
  };

  return (
    <div style={{ marginBottom: "2rem" }}>
      <button onClick={handleClick} disabled={loading}>
        {loading ? "Running Migration..." : "Run Migration"}
      </button>

      {result && (
        <div style={{ marginTop: "1rem" }}>
          <h3>✅ Migration Completed:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}

      {error && (
        <div style={{ color: "red", marginTop: "1rem" }}>
          ❌ {error}
        </div>
      )}
    </div>
  );
}
