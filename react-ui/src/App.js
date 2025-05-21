import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/home';
import TestResult from './pages/test_results';
import RunsList  from "./pages/RunsList";
import RunDetail from "./pages/RunDetail";


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/runs"        element={<RunsList />} />
        <Route path="/runs/:id"    element={<RunDetail />} />
        <Route path="/test-result" element={<TestResult />} />
      </Routes>
    </Router>
  );
}

export default App;
