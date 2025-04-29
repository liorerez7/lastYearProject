//-----------------------------
// 🔹 Imports + אייקונים – FRONTEND בלבד
// אין שום חיבור ל־Backend בחלק הזה
//-----------------------------
import React, { useState, useRef } from "react";
import { FaAws, FaGoogle, FaMicrosoft } from "react-icons/fa";
import { BiUpload, BiRun, BiTestTube, BiCloud } from "react-icons/bi";
import "./home.css";
import { useNavigate } from 'react-router-dom';

// UI ONLY: כאן רק עיצובי – אפשר לשנות את האייקונים
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

//-----------------------------
// 🔸 useState – קביעת מצב נוכחי
// כל המשתנים האלה משמשים גם ל־Backend בעתיד (שליחה לשרת)
//-----------------------------
export default function HomePage() {
  const clouds = ["AWS", "Google Cloud", "Azure"];
  const databases = ["MySQL", "PostgreSQL", "MongoDB"];
  const navigate = useNavigate();

  const [srcCloud, setSrcCloud] = useState("");
  const [dstCloud, setDstCloud] = useState("");
  const [srcDB, setSrcDB] = useState("");
  const [dstDB, setDstDB] = useState("");

  const [schemaFile, setSchema] = useState(null);
  const [dataFile, setData] = useState(null);

  const [loadingUpload, setLoadingUpload] = useState(false);
  const [uploadDone, setUploadDone] = useState(false);
  const [loadingMigration, setLoadingMigration] = useState(false);
  const [loadingTest, setLoadingTest] = useState(false);

  const schemaInputRef = useRef(null);
  const dataInputRef = useRef(null);

  const cloudReady = srcCloud && dstCloud && srcDB && dstDB;
  const filesReady = schemaFile && dataFile;
  const actionsReady = uploadDone;

  //-----------------------------
  // 🔸 UI Logic בלבד – פתיחת חלון קובץ
  //-----------------------------
  const handleSchemaAreaClick = () => schemaInputRef.current.click();
  const handleDataAreaClick = () => dataInputRef.current.click();

  const handleSchemaDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files?.[0]) setSchema(e.dataTransfer.files[0]);
  };
  const handleDataDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files?.[0]) setData(e.dataTransfer.files[0]);
  };

  const preventDefault = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  //-----------------------------
  // ✅ BACKEND: שליחת קבצים ל־/upload
  // נדרש קונטרולר FastAPI שמטפל בקובצי schema_file ו־data_file
  //-----------------------------
  async function handleUpload() {
    setLoadingUpload(true);
    const form = new FormData();
    form.append("schema_file", schemaFile);
    form.append("data_file", dataFile);

    try {
      const res = await fetch("http://localhost:8080/upload", { method: "POST", body: form });
      await res.json(); // הנחה שהתשובה מחזירה JSON
      setUploadDone(true);

      // ✅ הצגת הודעת הצלחה
      const notification = document.getElementById("success-notification");
      notification.classList.add("show");
      setTimeout(() => notification.classList.remove("show"), 3000);
    } catch (e) {
      console.error(e);
      const notification = document.getElementById("error-notification");
      notification.classList.add("show");
      setTimeout(() => notification.classList.remove("show"), 3000);
    } finally {
      setLoadingUpload(false);
    }
  }

  //-----------------------------
  // ✅ BACKEND: הפעלת מיגרציה
  // כרגע סימולציה בלבד, אבל בעתיד יקרה fetch ל־/migration
  //-----------------------------
  const handleRunMig = () => {
    setLoadingMigration(true);
    setTimeout(() => {
      setLoadingMigration(false);
      window.location.href = "/migration-result";
    }, 1500);
  };

  //-----------------------------
  // ✅ BACKEND: הרצת Benchmark
  // כנ"ל, צריך להחליף בעתיד ב־fetch ל־/test
  //-----------------------------
  const handleRunTest = async () => {
      setLoadingTest(true);
      try {
        const response = await fetch("http://localhost:8080/test/create-simple-test", {
          method: "POST",
        });
        const result = await response.json();
        navigate("/test-result", { state: { testData: result } }); // ⬅ שליחה ל־Result
      } catch (err) {
        console.error("❌ Failed to create test", err);
        alert("Failed to create benchmark test");
      } finally {
        setLoadingTest(false);
      }
    };

  //-----------------------------
  // 🔹 RETURN: קומפוננטת UI בלבד
  // מכילה Cloud Setup, Upload, כפתורים וכו׳
  // אין צורך להבין CSS, זה נטו עיצוב
  //-----------------------------
  return (
    <div className="home-container">
      <header className="header">
        <BiCloud className="logo-icon" />
        <h1>Cloud Database Migration Tool</h1>
        <p className="tagline">Seamlessly migrate and test your databases across cloud platforms</p>
      </header>

      {/* בחירת ענן ומסד נתונים – UI בלבד */}
      <div className="panel-grid">
        {/* SOURCE CARD */}
        <div className="cloud-card source-card">
          <h2 className="panel-title">Source Environment</h2>
          <div className="cloud-selection">
            <label htmlFor="srcCloud">Cloud Provider</label>
            <div className="select-wrapper">
              <select id="srcCloud" value={srcCloud} onChange={e => setSrcCloud(e.target.value)} className="cloud-select">
                <option value="">Select source cloud</option>
                {clouds.map(cloud => <option key={cloud} value={cloud}>{cloud}</option>)}
              </select>
              {srcCloud && <span className="cloud-icon">{cloudIcons[srcCloud]}</span>}
            </div>
          </div>

          <div className="db-selection">
            <label htmlFor="srcDB">Database Engine</label>
            <div className="select-wrapper">
              <select id="srcDB" value={srcDB} onChange={e => setSrcDB(e.target.value)} className="db-select" disabled={!srcCloud}>
                <option value="">Select database type</option>
                {databases.map(db => <option key={db} value={db}>{db}</option>)}
              </select>
              {srcDB && <span className="db-icon">{dbIcons[srcDB]}</span>}
            </div>
          </div>
        </div>

        {/* DESTINATION CARD */}
        <div className="cloud-card destination-card">
          <h2 className="panel-title">Destination Environment</h2>
          <div className="cloud-selection">
            <label htmlFor="dstCloud">Cloud Provider</label>
            <div className="select-wrapper">
              <select id="dstCloud" value={dstCloud} onChange={e => setDstCloud(e.target.value)} className="cloud-select">
                <option value="">Select target cloud</option>
                {clouds.map(cloud => <option key={cloud} value={cloud}>{cloud}</option>)}
              </select>
              {dstCloud && <span className="cloud-icon">{cloudIcons[dstCloud]}</span>}
            </div>
          </div>

          <div className="db-selection">
            <label htmlFor="dstDB">Database Engine</label>
            <div className="select-wrapper">
              <select id="dstDB" value={dstDB} onChange={e => setDstDB(e.target.value)} className="db-select" disabled={!dstCloud}>
                <option value="">Select database type</option>
                {databases.map(db => <option key={db} value={db}>{db}</option>)}
              </select>
              {dstDB && <span className="db-icon">{dbIcons[dstDB]}</span>}
            </div>
          </div>
        </div>
      </div>

      {/* העלאת קבצים – נטו עיצוב + handler */}
      {cloudReady && (
        <div className="upload-section">
          <h2 className="section-title">
            <BiUpload className="section-icon" />
            Upload SQL Files
          </h2>

          <div className="upload-grid">
            {/* schema file */}
            <div className={`drop-box ${schemaFile ? 'has-file' : ''}`}
                 onClick={handleSchemaAreaClick}
                 onDrop={handleSchemaDrop}
                 onDragOver={preventDefault}
                 onDragEnter={preventDefault}>
              <div className="drop-content">
                <div className="file-icon">📄</div>
                <h3>Schema Structure</h3>
                <p className="drop-instruction">
                  {schemaFile ? schemaFile.name : "Drop schema.sql or click"}
                </p>
                <input type="file" ref={schemaInputRef} className="file-input" accept=".sql"
                       onChange={e => setSchema(e.target.files[0])} />
                {schemaFile && (
                  <div className="file-info">
                    <span className="file-size">{(schemaFile.size / 1024).toFixed(1)} KB</span>
                  </div>
                )}
              </div>
            </div>

            {/* data file */}
            <div className={`drop-box ${dataFile ? 'has-file' : ''}`}
                 onClick={handleDataAreaClick}
                 onDrop={handleDataDrop}
                 onDragOver={preventDefault}
                 onDragEnter={preventDefault}>
              <div className="drop-content">
                <div className="file-icon">📊</div>
                <h3>Database Content</h3>
                <p className="drop-instruction">
                  {dataFile ? dataFile.name : "Drop data.sql or click"}
                </p>
                <input type="file" ref={dataInputRef} className="file-input" accept=".sql"
                       onChange={e => setData(e.target.files[0])} />
                {dataFile && (
                  <div className="file-info">
                    <span className="file-size">{(dataFile.size / 1024).toFixed(1)} KB</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* כפתור העלאה ל־Backend */}
          <div className="upload-action">
            <button className={`upload-btn ${loadingUpload ? 'loading' : ''}`}
                    disabled={!filesReady || loadingUpload}
                    onClick={handleUpload}>
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

      {/* פעולות לאחר ההעלאה – מיגרציה / בדיקה */}
      {actionsReady && (
        <div className="actions-section">
          <button className={`action-btn blue ${loadingMigration ? 'loading' : ''}`}
                  disabled={loadingMigration || loadingTest}
                  onClick={handleRunMig}>
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

          <button className={`action-btn green ${loadingTest ? 'loading' : ''}`}
                  disabled={loadingMigration || loadingTest}
                  onClick={handleRunTest}>
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
      )}

      {/* הודעות הצלחה/שגיאה – עיצוב בלבד */}
      <div id="success-notification" className="notification success">
        Files uploaded successfully ✅
      </div>
      <div id="error-notification" className="notification error">
        Upload failed. Please try again ❌
      </div>
    </div>
  );
}
