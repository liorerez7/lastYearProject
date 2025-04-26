import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/home';
import TestResult from './pages/test_results'; // ⬅️ NEW page

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/test-result" element={<TestResult />} />
      </Routes>
    </Router>
  );
}

export default App;
