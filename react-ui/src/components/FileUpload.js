import React, { useState } from 'react';

export default function FileUpload({ onUpload }) {
  const [schemaFile, setSchemaFile] = useState(null);
  const [dataFile, setDataFile] = useState(null);

  const handleSchemaChange = (event) => {
    setSchemaFile(event.target.files[0]);
  };

  const handleDataChange = (event) => {
    setDataFile(event.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!schemaFile || !dataFile) {
      alert("Please select both schema.sql and data.sql files!");
      return;
    }

    const formData = new FormData();
    formData.append("schema_file", schemaFile);
    formData.append("data_file", dataFile);

    onUpload(formData);
  };

  return (
    <div style={{ border: "2px dashed #ccc", padding: "2rem", borderRadius: "8px", textAlign: "center", marginBottom: "2rem" }}>
      <h3>📂 Upload your SQL files</h3>

      <div style={{ marginBottom: "1rem" }}>
        <p><strong>Schema.sql:</strong></p>
        <input type="file" accept=".sql" onChange={handleSchemaChange} />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <p><strong>Data.sql:</strong></p>
        <input type="file" accept=".sql" onChange={handleDataChange} />
      </div>

      <button onClick={handleSubmit}>Upload Files</button>
    </div>
  );
}
