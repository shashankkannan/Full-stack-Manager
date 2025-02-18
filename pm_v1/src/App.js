import './App.css';
import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Setupapp from "./components/Setupapp";
import Test from './components/Test';
import Bcktest from './components/Bcktest';

function App() {

  return (
    <Router>
      <div>
        <style>
          {`
            /* Basic reset for margin and padding */
            * {
              margin: 0;
              padding: 0;
              box-sizing: border-box;
            }

            /* Header styling */
            .navbar {
              background-color: #2c3e50;
              padding: 10px 20px;
              box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            }

            /* Navigation styling */
            nav {
              display: flex;
              justify-content: flex-end; /* Align the links to the right */
              gap: 20px; /* Space between the links */
            }

            /* Link styling */
            .nav-link {
              color: #ecf0f1;
              text-decoration: none;
              font-size: 16px;
              font-weight: 600;
              padding: 10px 15px;
              border-radius: 5px;
              transition: transform 0.2s ease, box-shadow 0.2s ease;
            }

            /* Link hover effects */
            .nav-link:hover {
              transform: translateY(-3px);
              box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.2);
              background-color: #34495e;
            }

            /* Adding 3D effect with subtle shadows */
            .nav-link:active {
              transform: translateY(1px);
              box-shadow: 0px 2px 3px rgba(0, 0, 0, 0.1);
            }
          `}
        </style>

        <header className="navbar">
          <nav>
            <Link to="/" className="nav-link">Set up App</Link>
            <Link to="/test" className="nav-link">Set Up Back-end</Link>
            <Link to="/bcktest" className="nav-link">Test Back-end</Link>
          </nav>
        </header>
        
        <Routes>
          <Route path="/" element={<Setupapp />} />
          <Route path="/test" element={<Test />} />
          <Route path="/bcktest" element={<Bcktest />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
