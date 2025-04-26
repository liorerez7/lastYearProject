import React, { useState } from 'react';
import { createSimpleTest } from '../api/test_api';
import { useNavigate } from 'react-router-dom';

export default function CreateSimpleTestButton() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleClick = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await createSimpleTest();
      navigate('/test-result', { state: { testData: data } });  // pass data to TestResult page
    } catch (err) {
      setError(err.message);
    }

    setLoading(false);
  };

  return (
    <div style={{ marginBottom: "2rem" }}>
      <button onClick={handleClick} disabled={loading}>
        {loading ? "Creating Test..." : "Create Simple Test"}
      </button>
      {error && <p style={{ color: "red" }}>❌ {error}</p>}
    </div>
  );
}
