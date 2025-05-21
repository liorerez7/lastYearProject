import React from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "react-query";
import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8080";

const getExecutions = async (test_id) => {
  const res = await axios.get(`${API_URL}/executions?test_id=${test_id}`);
  return res.data;
};

const RunResults = () => {
  const { test_id } = useParams(); // שמנו בפרמטר של ה־URL
  const { data, isLoading, isError } = useQuery(["executions", test_id], () => getExecutions(test_id));

  if (isLoading) return <div>טוען תוצאות...</div>;
  if (isError) return <div>שגיאה בטעינת התוצאות</div>;

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">תוצאות גולמיות</h1>
      <pre style={{ background: "#f0f0f0", padding: "1rem", overflowX: "auto" }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default RunResults;
