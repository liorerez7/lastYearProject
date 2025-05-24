import React from "react";
import { useRunsList } from "../state/queries";
import RunCard from "../components/RunCard";

const RunsList = () => {
  const { data: runs, isLoading, isError } = useRunsList();

  if (isLoading) return <div className="flex justify-center h-64">טוען…</div>;
  if (isError)  return <div className="text-red-600 p-4">שגיאה</div>;

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">היסטוריית ריצות</h1>
      {runs.length ? runs.map(r => <RunCard key={r.id} run={r}/>)
        : <p>אין ריצות.</p>}
    </div>
  );
};
export default RunsList;
