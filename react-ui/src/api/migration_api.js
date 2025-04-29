export async function runMigration() {
  const response = await fetch("http://localhcost:8080/migration/run-migration", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      source: "mysql",
      destination: "postgres",
      schema_name: "employees"
    })
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Migration failed");
    console.log("Error:", data.detail || "Migration failed");
  }
  return data;
}
