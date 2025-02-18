import axios from 'axios';
import React, { useEffect, useState } from "react";
import urls from '../config';
    
function Setupapp() {
    const [message, setMessage] = useState('');
    const [appName, setAppName] = useState('');
    const [loading, setLoading] = useState(false);
    const [portsData, setPortsData] = useState([]);

    const reservedNames = [
        "react", "react-dom", "create-react-app", "node", "npm", "express", "vue"
    ];

    useEffect(() => {
        axios.get(`${urls.flask}`)
            .then(response => {
                setMessage(response.data.message);
            })
            .catch(error => {
                setMessage(`${error} : Message from React: Backend not set up!`);
            });

            fetchPortsData();
    }, []);

    const fetchPortsData = () => {
        axios.get(`${urls.flask}/get-ports`)
            .then(response => {
                setPortsData(response.data.ports); // Set the list of ports and their states
            })
            .catch(error => {
                setMessage(`${error} : Message from React: Backend not set up!`);
            });
    };

    const isValidAppName = (name) => {
        const regex = /^[a-z0-9]+([-_][a-z0-9]+)*$/;
        return regex.test(name) && !reservedNames.includes(name);
    };
    const generateSuggestedAppName = (appName)=> {
        // Convert to lowercase
        console.log(appName)
        let suggestedName = appName.toLowerCase();
        
        // Replace spaces with hyphens
        suggestedName = suggestedName.replace(/\s+/g, '-');
        
        // Remove special characters (except hyphens)
        suggestedName = suggestedName.replace(/[^a-z0-9-]/g, '');
        
        return suggestedName;
    }
    const handleCreateApp = () => {
        if (!appName.trim()) {
            alert("Please enter a valid app name!\n\n" +
                  "Here are some guidelines for naming your app:\n" +
                  "1. Use lowercase letters: e.g., my-react-app\n" +
                  "2. Use hyphens to separate words: e.g., my-react-project\n" +
                  "3. Avoid spaces, special characters, and reserved words: Don't use spaces or characters like @, #, $, %, &, etc. Avoid system and programming reserved words (e.g., CON, PRN, exports, require).\n" +
                  "4. Keep it short and descriptive: Choose a name that’s easy to remember and reflects the project’s purpose.\n\n" +
                  "Make sure the app name follows these rules to avoid errors.");
            return;
        }
        if (!isValidAppName(appName)) {
            alert("Invalid app name! Follow the naming rules:\n\n" +
                  "1. Use lowercase letters: e.g., my-react-app\n" +
                  "2. Use hyphens to separate words: e.g., my-react-project\n" +
                  "3. Avoid spaces, special characters, and reserved words: Don't use spaces or characters like @, #, $, %, &, etc. Avoid system and programming reserved words (e.g., CON, PRN, exports, require).\n" +
                  "4. Keep it short and descriptive: Choose a name that’s easy to remember and reflects the project’s purpose."+
                  "\nSuggested app name:\n" + generateSuggestedAppName(appName)+" ");
            return;
        }

        setLoading(true);
        setMessage("⏳ Creating app... Please wait.");

        axios.post(`${urls.flask}/create-app`, { app_name: appName })
        .then(response => {
            // Set success message after app creation
            setMessage(`✅ App "${appName}" created successfully!`);

            // Fetch the updated ports data after app creation
            fetchPortsData();
        }).catch(error => setMessage(`❌ Error creating app: ${error.message}`))
            .finally(() => setLoading(false));
        
    };

    const handlestart = (appName, ap, ps) => {
        if(ps ==="stopped"){
            axios.post(`${urls.flask}/start-app`, { app_name: appName, app_port: ap })
            .then(response => {
                alert(response.data.message);
                fetchPortsData();
            })
            .catch(error => {
                alert(`❌ Error starting app: ${error.response?.data?.error || error.message}`);
            });
        }
        else{
            alert("The app is already running!")
            const newTabUrl = `http://localhost:${ap}`;
            window.open(newTabUrl, "_blank");
        }
        
    };

    const handlestop = async (an, ap, ps) => {
        try {
            alert(`${an} - ${ap} - App Stop function using port (We get the process id and kill it)`);
    
            const response = await fetch(`${urls.flask}/stop_process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ port: ap }), // Send the port as JSON to the backend
            });
    
            const data = await response.json();
    
            if (response.ok) {
                alert(data.message); // Show success message
            } else {
                alert(data.error || data.message); // Show error message
            }
        } catch (error) {
            console.error("Error stopping the process:", error);
            alert("An error occurred while stopping the process.");
        }
    };

    const openappinvs = (appName) => {
        axios.post(`${urls.flask}/open-in-vscode`, { app_name: appName })
            .then(response => {
                alert(response.data.message);
            })
            .catch(error => {
                alert(`❌ Error: ${error.response?.data?.error || error.message}`);
            });
    };

    return (
        <div className="App">
            <header className="App-header">
                <h2>Setup Your React App</h2>
                <input
                    type="text"
                    placeholder="Enter app name"
                    value={appName}
                    onChange={(e) => setAppName(e.target.value)}
                    style={{
                        padding: '10px',
                        fontSize: '16px',
                        marginBottom: '10px',
                        marginTop: '15px'
                    }}
                    disabled={loading}
                />
                <br />
                <button 
                    onClick={handleCreateApp} 
                    style={{
                        padding: '10px 20px',
                        fontSize: '16px',
                        cursor: 'pointer',
                        backgroundColor: loading ? '#ccc' : '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        marginBottom: '10px',
                        marginTop: '15px'
                    }}
                    disabled={loading}
                >
                    {loading ? "⏳ Creating..." : "Create React App"}
                </button>
                <p style={{
                        padding: '10px',
                        fontSize: '16px',
                        marginBottom: '10px',
                        marginTop: '15px'
                    }}>{message}</p>

                <h3 style={{
                        padding: '10px',
                        marginBottom: '10px',
                        marginTop: '15px'
                    }}>Currently Reserved Ports:</h3>
<div style={{ maxHeight: '300px', maxWidth: '100vw', width: '80%', overflowY: 'auto', border: '1px solid #ccc', borderRadius: '5px' }}>
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
            <tr>
                <th>Port</th>
                <th>App Name</th>
                <th>State</th>
                <th>Actions</th> {/* Add a new column for buttons */}
            </tr>
        </thead>
        <tbody>
            {portsData.length > 0 ? (
                portsData.map((portInfo, index) => (
                    <tr key={index}>
                        <td>{portInfo.port}</td>
                        <td>{portInfo.app_name}</td>
                        <td>{portInfo.state}</td>
                        <td>
                            <button
                                style={{
                                    padding: '5px 10px',
                                    margin: '0 5px',
                                    backgroundColor: '#28a745',
                                    color: 'white',
                                    border: 'none',
                                }}
                                onClick={() => {handlestart(portInfo.app_name, portInfo.port, portInfo.state);}}
                            >
                                Start
                            </button>
                            {/* <button
                                style={{
                                    padding: '5px 10px',
                                    margin: '0 5px',
                                    backgroundColor: '#dc3545',
                                    color: 'white',
                                    border: 'none',
                                }}
                                onClick={() => {handlestop(portInfo.app_name, portInfo.port, portInfo.state);}}
                            >
                                Stop
                            </button> */}
                            <button
                                style={{
                                    padding: '5px 10px',
                                    margin: '0 5px',
                                    backgroundColor: '#007bff',
                                    color: 'white',
                                    border: 'none',
                                }}
                                onClick={() => {openappinvs(portInfo.app_name);}}
                            >
                                Open in VS
                            </button>
                        </td>
                    </tr>
                ))
            ) : (
                <tr>
                    <td colSpan="4">No ports found.</td> {/* Adjust colspan for the new button column */}
                </tr>
            )}
        </tbody>
    </table>
    </div>
            </header>
        </div>
    );
}

export default Setupapp;
