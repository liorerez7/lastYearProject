export async function createSimpleTest() {
  const response = await fetch("http://localhost:8080/test/create-simple-test", {
    method: "POST",
    headers: { "Content-Type": "application/json" }
  });
  const data = await response.json();
  if (!response.ok) {
    console.log("Error:", data.detail || "Test creation failed");
    throw new Error(data.detail || "Test creation failed");
  }
  return data;
}
