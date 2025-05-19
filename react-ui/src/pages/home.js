import React, { useState, useRef } from "react";
import { FaAws, FaGoogle, FaMicrosoft } from "react-icons/fa";
import { BiUpload, BiRun, BiTestTube, BiCloud, BiTable } from "react-icons/bi";
import { BiAnalyse } from "react-icons/bi";
import "./home.css";

const cloudIcons = {
  "AWS": <FaAws size={24} />,
  "Google Cloud": <FaGoogle size={24} />,
  "Azure": <FaMicrosoft size={24} />
};

const dbIcons = {
  "MySQL": "🗄️",
  "PostgreSQL": "🐘",
  "MongoDB": "🍃"
};

export default function HomePage() {
  /* ─────────────── state ─────────────── */
  const clouds = ["AWS", "Google Cloud", "Azure"];
  const databases = ["MySQL", "PostgreSQL", "MongoDB"];
  const [availableTables, setAvailableTables] = useState([]);
  const testTypes = ["Basic Queries", "Advanced Workload", "Balanced Suite"];

  const [srcCloud, setSrcCloud] = useState("");
  const [dstCloud, setDstCloud] = useState("");
  const [srcDB, setSrcDB] = useState("");
  const [dstDB, setDstDB] = useState("");

  const [schemaFile, setSchema] = useState(null);
  const [dataFile, setData] = useState(null);

  const [loadingUpload, setLoadingUpload] = useState(false);
  const [uploadDone, setUploadDone] = useState(false);

  const [tablesChosen, setTablesChosen] = useState([]);
  const [testLevel, setTestLevel] = useState("");

  const [loadingMigration, setLoadingMigration] = useState(false);
  const [loadingTest, setLoadingTest] = useState(false);

  const schemaInputRef = useRef(null);
  const dataInputRef = useRef(null);

  /* ─────────── derived flags ─────────── */
  const cloudReady = srcCloud && dstCloud && srcDB && dstDB;
  const filesReady = schemaFile && dataFile;
  const tableSelectionReady = tablesChosen.length > 0;
  const testTypeReady = testLevel !== "";
  const actionsReady = uploadDone && tableSelectionReady && testTypeReady;

  /* ─────────────── handlers ─────────────── */
  const handleSchemaAreaClick = () => {
    schemaInputRef.current.click();
  };

  const handleDataAreaClick = () => {
    dataInputRef.current.click();
  };

  const handleSchemaDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSchema(e.dataTransfer.files[0]);
    }
  };

  const handleDataDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setData(e.dataTransfer.files[0]);
    }
  };

  const preventDefault = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const toggleTable = (table) => {
    setTablesChosen(prev =>
      prev.includes(table)
        ? prev.filter(t => t !== table)
        : [...prev, table]
    );
  };

  const selectTestType = (type) => {
    setTestLevel(type);
  };

  async function handleUpload() {
    setLoadingUpload(true);
    const form = new FormData();
    form.append("schema_file", schemaFile);
    form.append("data_file", dataFile);

    try {
      const res = await fetch("http://localhost:8080/upload", { method: "POST", body: form });
      const result = await res.json();
      setAvailableTables(result.tables || []);
      setUploadDone(true);
      setTimeout(() => {
        // Simulating success notification instead of alert
        const notification = document.getElementById("success-notification");
        notification.classList.add("show");
        setTimeout(() => {
          notification.classList.remove("show");
        }, 3000);
      }, 500);
    } catch (e) {
      console.error(e);
      setTimeout(() => {
        // Simulating error notification instead of alert
        const notification = document.getElementById("error-notification");
        notification.classList.add("show");
        setTimeout(() => {
          notification.classList.remove("show");
        }, 3000);
      }, 500);
    } finally {
      setLoadingUpload(false);
    }
  }

  const handleRunMig = () => {
    setLoadingMigration(true);
    // Simulating API call
    setTimeout(() => {
      setLoadingMigration(false);
      window.location.href = "/migration-result"; // Redirect to results page
    }, 1500);
  };

 const handleRunTest = async () => {
  setLoadingTest(true);
  try {
    const res = await fetch("http://localhost:8080/test/create-simple-test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ test_type: testLevel })
    });
    const result = await res.json();
    console.log("✅ Test response:", result);
    window.location.href = "/test-result";
  } catch (e) {
    console.error("🔥 Test run failed:", e);
  } finally {
    setLoadingTest(false);
  }
};


  return (
    <div className="home-container">
      <header className="header">
        <BiCloud className="logo-icon" />
        <h1>Cloud Database Migration Tool</h1>
        <p className="tagline">Seamlessly migrate and test your databases across cloud platforms</p>
      </header>

      {/* Progress Indicator */}
      <div className="progress-tracker">
        <div className={`progress-step ${cloudReady ? 'complete' : 'active'}`}>
          <div className="step-icon">1</div>
          <div className="step-label">Cloud Setup</div>
        </div>
        <div className={`progress-step ${cloudReady ? (uploadDone ? 'complete' : 'active') : ''}`}>
          <div className="step-icon">2</div>
          <div className="step-label">Upload Files</div>
        </div>
        <div className={`progress-step ${uploadDone ? (tableSelectionReady ? 'complete' : 'active') : ''}`}>
          <div className="step-icon">3</div>
          <div className="step-label">Select Tables</div>
        </div>
        <div className={`progress-step ${tableSelectionReady ? (testTypeReady ? 'complete' : 'active') : ''}`}>
          <div className="step-icon">4</div>
          <div className="step-label">Choose Test</div>
        </div>
      </div>

      <div className="panel-grid">
        {/* Source Cloud Panel */}
        <div className="cloud-card source-card">
          <h2 className="panel-title">Source Environment</h2>
          <div className="cloud-selection">
            <label htmlFor="srcCloud">Cloud Provider</label>
            <div className="select-wrapper">
              <select
                id="srcCloud"
                value={srcCloud}
                onChange={e => setSrcCloud(e.target.value)}
                className="cloud-select"
              >
                <option value="">Select source cloud</option>
                {clouds.map(cloud => (
                  <option key={cloud} value={cloud}>
                    {cloud}
                  </option>
                ))}
              </select>
              {srcCloud && (
                <span className="cloud-icon">
                  {cloudIcons[srcCloud]}
                </span>
              )}
            </div>
          </div>

          <div className="db-selection">
            <label htmlFor="srcDB">Database Engine</label>
            <div className="select-wrapper">
              <select
                id="srcDB"
                value={srcDB}
                onChange={e => setSrcDB(e.target.value)}
                className="db-select"
                disabled={!srcCloud}
              >
                <option value="">Select database type</option>
                {databases.map(db => (
                  <option key={db} value={db}>
                    {db}
                  </option>
                ))}
              </select>
              {srcDB && (
                <span className="db-icon">
                  {dbIcons[srcDB]}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Destination Cloud Panel */}
        <div className="cloud-card destination-card">
          <h2 className="panel-title">Destination Environment</h2>
          <div className="cloud-selection">
            <label htmlFor="dstCloud">Cloud Provider</label>
            <div className="select-wrapper">
              <select
                id="dstCloud"
                value={dstCloud}
                onChange={e => setDstCloud(e.target.value)}
                className="cloud-select"
              >
                <option value="">Select target cloud</option>
                {clouds.map(cloud => (
                  <option key={cloud} value={cloud}>
                    {cloud}
                  </option>
                ))}
              </select>
              {dstCloud && (
                <span className="cloud-icon">
                  {cloudIcons[dstCloud]}
                </span>
              )}
            </div>
          </div>

          <div className="db-selection">
            <label htmlFor="dstDB">Database Engine</label>
            <div className="select-wrapper">
              <select
                id="dstDB"
                value={dstDB}
                onChange={e => setDstDB(e.target.value)}
                className="db-select"
                disabled={!dstCloud}
              >
                <option value="">Select database type</option>
                {databases.map(db => (
                  <option key={db} value={db}>
                    {db}
                  </option>
                ))}
              </select>
              {dstDB && (
                <span className="db-icon">
                  {dbIcons[dstDB]}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* File Upload Section - visible only when cloud setup is done */}
      {cloudReady && (
        <div className="upload-section">
          <h2 className="section-title">
            <BiUpload className="section-icon" />
            Upload SQL Files
          </h2>

          <div className="upload-grid">
            {/* Schema File Upload */}
            <div
              className={`drop-box ${schemaFile ? 'has-file' : ''}`}
              onClick={handleSchemaAreaClick}
              onDrop={handleSchemaDrop}
              onDragOver={preventDefault}
              onDragEnter={preventDefault}
            >
              <div className="drop-content">
                <div className="file-icon">📄</div>
                <h3>Schema Structure</h3>
                <p className="drop-instruction">
                  {schemaFile ? schemaFile.name : "Drop schema.sql or click"}
                </p>
                <input
                  type="file"
                  ref={schemaInputRef}
                  className="file-input"
                  accept=".sql"
                  onChange={e => setSchema(e.target.files[0])}
                />
                {schemaFile && (
                  <div className="file-info">
                    <span className="file-size">
                      {(schemaFile.size / 1024).toFixed(1)} KB
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Data File Upload */}
            <div
              className={`drop-box ${dataFile ? 'has-file' : ''}`}
              onClick={handleDataAreaClick}
              onDrop={handleDataDrop}
              onDragOver={preventDefault}
              onDragEnter={preventDefault}
            >
              <div className="drop-content">
                <div className="file-icon">📊</div>
                <h3>Database Content</h3>
                <p className="drop-instruction">
                  {dataFile ? dataFile.name : "Drop data.sql or click"}
                </p>
                <input
                  type="file"
                  ref={dataInputRef}
                  className="file-input"
                  accept=".sql"
                  onChange={e => setData(e.target.files[0])}
                />
                {dataFile && (
                  <div className="file-info">
                    <span className="file-size">
                      {(dataFile.size / 1024).toFixed(1)} KB
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="upload-action">
            <button
              className={`upload-btn ${loadingUpload ? 'loading' : ''}`}
              disabled={!filesReady || loadingUpload}
              onClick={handleUpload}
            >
              {loadingUpload ? (
                <>
                  <span className="spinner"></span>
                  <span>Uploading...</span>
                </>
              ) : (
                <>
                  <BiUpload className="btn-icon" />
                  <span>Upload Files</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Table Selection Section - visible only after file upload */}
      {uploadDone && (
        <div className="config-card">
          <div className="config-header">
            <BiTable className="config-icon" />
            <h2>Table Selection</h2>
          </div>
          <p className="config-description">Select tables to include in the testing process</p>

          <div className="table-checkboxes">
            {availableTables.map((table) => (
              <label key={table} className={tablesChosen.includes(table) ? 'selected' : ''}>
                <input
                  type="checkbox"
                  checked={tablesChosen.includes(table)}
                  onChange={() => toggleTable(table)}
                />
                <span className="checkbox-label">{table}</span>
                <span className={`table-badge ${tablesChosen.includes(table) ? 'selected' : ''}`}>
                  {tablesChosen.includes(table) ? '✓' : ''}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Test Type Selection - Appears only when tables are selected */}
      {uploadDone && tableSelectionReady && (
        <div className="config-card test-type-card">
          <div className="config-header">
            <BiAnalyse className="config-icon" />
            <h2>Test Complexity</h2>
          </div>
          <p className="config-description">Select the complexity level for the benchmark test</p>

          <div className="test-type-selector">
            {testTypes.map((type) => (
              <button
                key={type}
                className={`test-type-btn ${testLevel === type ? 'selected' : ''}`}
                onClick={() => selectTestType(type)}
              >
                <span className="test-type-name">{type}</span>
                <span className="test-type-description">
                  {type === 'EASY' ? 'Simple query testing' :
                   type === 'HARD' ? 'Complex joins & aggregations' :
                   'Balanced mix of queries'}
                </span>
                {testLevel === type && <span className="test-selected-mark">✓</span>}
              </button>
            ))}
          </div>
        </div>
      )}

      {actionsReady && (
        <>
        <div className="summary-panel">
          <div className="config-header">
            <BiAnalyse className="config-icon" />
            <h2>Migration Summary</h2>
          </div>
          <div className="summary-details">
            <div className="summary-item">
              <span className="summary-label">Source:</span>
              <span className="summary-value">{srcCloud} ({srcDB})</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Destination:</span>
              <span className="summary-value">{dstCloud} ({dstDB})</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Tables:</span>
              <span className="summary-value">{tablesChosen.length} selected</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Test Type:</span>
              <span className="summary-value">{testLevel}</span>
            </div>
          </div>
        </div>

          <div className="actions-section">
            <button
              className={`action-btn blue ${loadingMigration ? 'loading' : ''}`}
              disabled={loadingMigration || loadingTest}
              onClick={handleRunMig}
            >
              {loadingMigration ? (
                <>
                  <span className="spinner white"></span>
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <BiRun className="btn-icon" />
                  <span>Run Migration</span>
                </>
              )}
            </button>

            <button
              className={`action-btn green ${loadingTest ? 'loading' : ''}`}
              disabled={loadingMigration || loadingTest}
              onClick={handleRunTest}
            >
              {loadingTest ? (
                <>
                  <span className="spinner white"></span>
                  <span>Testing...</span>
                </>
              ) : (
                <>
                  <BiTestTube className="btn-icon" />
                  <span>Run Benchmark Test</span>
                </>
              )}
            </button>
          </div>
        </>
      )}

      {/* Notifications */}
      <div id="success-notification" className="notification success">
        Files uploaded successfully ✅
      </div>
      <div id="error-notification" className="notification error">
        Upload failed. Please try again ❌
      </div>
    </div>
  );
}