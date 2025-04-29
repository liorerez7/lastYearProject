//import React from 'react';
//import CreateSimpleTestButton from '../components/CreateSimpleTestButton';
//import RunMigrationButton from '../components/RunMigrationButton';
//
//export default function Home() {
//  return (
//    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
//      <h1>Database Migration & Test UI</h1>
//      <CreateSimpleTestButton />
//      <RunMigrationButton />
//    </div>
//  );
//}
import React from 'react';
import CreateSimpleTestButton from '../components/CreateSimpleTestButton';
import RunMigrationButton from '../components/RunMigrationButton';
import FileUpload from '../components/FileUpload';

export default function Home() {
  const handleUpload = async (formData) => {
    try {
      const response = await fetch("http://localhost:8080/upload", {
        method: "POST",
        body: formData
      });
      const data = await response.json();
      console.log("✅ Files uploaded:", data);
      alert("Files uploaded successfully!");
    } catch (error) {
      console.error("❌ Error uploading files:", error);
      alert("Error uploading files.");
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>Database Migration & Test UI</h1>
      <FileUpload onUpload={handleUpload} />
      <CreateSimpleTestButton />
      <RunMigrationButton />
    </div>
  );
}
