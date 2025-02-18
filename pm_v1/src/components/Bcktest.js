import { useState, useEffect } from "react";
import axios from "axios";

function Bcktest() {
  const [bckmsg, setbckmsg] = useState('');
  const [po, setpo] = useState('');

  const getbck = () => {
    const urld = `http://127.0.0.1:${po}`;
    axios.get(`${urld}`)
      .then((response) => {
        setbckmsg(response.data.message);
      }).catch((error) => {
        setbckmsg(`${error}: Backend not set up yet`);
      });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h2 style={{
          padding: '10px',
          marginBottom: '10px',
          marginTop: '15px'
        }}>Port </h2>
        
        <input 
          style={{
            padding: '10px',
            marginBottom: '10px',
            marginTop: '15px'
          }} 
          type="text" 
          onChange={(e) => { setpo(e.target.value); }} 
        />

        <button
          style={{
            padding: "10px",
            cursor: "pointer",
            transition: "transform 0.1s ease",
            marginTop: "15px",
            marginBottom: "10px"
          }}
          onClick={() => { getbck(); }}
        >
          Check backend
        </button>

        <p style={{
          padding: '15px',
          backgroundColor: '#f4f4f4', // Light gray background for better visibility
          border: '1px solid #ddd',
          borderRadius: '5px',
          width: '80%',
          margin: '10px auto',
          fontFamily: 'monospace', // Monospace font for code
          fontSize: '14px', // Adjusted font size for better readability
          color: '#333', // Dark text color for better contrast
          whiteSpace: 'pre-wrap', // Preserve new lines and wrap long lines
          wordWrap: 'break-word',
          boxShadow: '0px 4px 8px rgba(0,0,0,0.1)',
        }}>
          <strong>Note:</strong> Use this in your React frontend to connect to the backend:
          <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
{`useEffect(() => {
    axios.get("http://your-api-url:your-port")
        .then(response => {
            setMessage(response.data.message);
        })
        .catch(error => {
            setMessage(\`\${error} : Message from React: Backend not set up!\`);
        });
}, []);`}
          </pre>
        </p>

        <p>Msg from Backend Setup: {bckmsg}</p>

      </header>
    </div>
  );
}

export default Bcktest;
