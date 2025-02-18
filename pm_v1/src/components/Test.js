import React, { useEffect, useState } from 'react';
import axios from 'axios';
import urls from '../config';

function BackendManager() {
    const [ports, setPorts] = useState([]);
    const [msg, setMsg] = useState('');
    const [backendName, setBackendName] = useState('');
    const [selectedBackends, setSelectedBackends] = useState([]);

    useEffect(() => {
        fetchPorts();
    }, []);

    const fetchPorts = () => {
        axios.get(`${urls.flask}/get-ports-bck`)
            .then(response => {
                if (response.data.ports) {
                    setPorts(response.data.ports);
                }
            })
            .catch(error => {
                console.error("Error fetching ports:", error);
            });
    };

    const handleCheckboxChange = (backend) => {
        setSelectedBackends((prev) =>
            prev.includes(backend)
                ? prev.filter(item => item !== backend)  // Remove if already selected
                : [...prev, backend]  // Add if not selected
        );
    };

    const clickButton = () => {
        if (selectedBackends.length === 0) {
            alert("Please select at least one backend option.");
            return;
        }
        if (backendName.length === 0) {
            alert("Please give an alias name.");
            return;
        }

        axios.get(`${urls.flask}/choice_backend`, {
            params: { backend: selectedBackends.join(", "), backend_name: backendName }
        })
        .then(response => {
            setMsg(response.data.message);
            const detailsFormatted = response.data.details.map(item =>
                `Backend: ${item.backend}, App Name: ${item.app_name}, Unique ID: ${item.unique_id}, Port: ${item.port}, Folder Name: ${item.Folder_name}`
            ).join("\n");
            alert(`Backend Name: ${backendName}\nSelected Backends: ${selectedBackends.join(", ")}\n${response.data.message}: ${detailsFormatted} from Flask Backend`);
        })
        .catch(error => {
            setMsg(`${error} : Message from React: Backend not set up!`);
        });
    };

    const handleStart = (bck, folderPath) => {
        if (bck === "Flask"){
            console.log(folderPath)
        axios.post(`${urls.flask}/start-backend-flask`, { folder_path: folderPath })
            .then(response => {
                alert(response.data.message);
            })
            .catch(error => {
                alert("Failed to start backend: " + (error.response?.data?.error || error.message));
            });
        }
        else if (bck === "Django"){
            axios.post(`${urls.flask}/start-backend-django`, { folder_path: folderPath })
            .then(response => {
                alert(response.data.message);
            })
            .catch(error => {
                alert("Failed to start backend: " + (error.response?.data?.error || error.message));
            });
        
        }
        else if (bck === "Express") {
            console.log(folderPath);
            axios.post(`${urls.flask}/start-backend-express`, { folder_path: folderPath })
                .then(response => {
                    alert(response.data.message);
                })
                .catch(error => {
                    alert("Failed to start Express backend: " + (error.response?.data?.error || error.message));
                });
        }
    };
    const handleInstructions = (folderPath, port, appname, bck, uq) => {
        let instructions = `Setup Instructions:\nApp Name: ${appname}${uq}\nPort: ${port}\nBackend type: ${bck}\n\n`;
    
        if (bck.toLowerCase() === "flask") {
            instructions += `The Flask backend has already been set up.\n\n`;
            instructions += `To start the server, follow these steps:\n`;
            instructions += `1. Navigate to ${folderPath}\n`;
            instructions += `2. Activate the virtual environment:\n`;
            instructions += `   - Windows: venv\\Scripts\\activate\n`;
            instructions += `   - Mac/Linux: source venv/bin/activate\n`;
            instructions += `3. Run the server:\n`;
            instructions += `   python app.py\n\n`;
            instructions += `Or, press the "Start" button to automatically open the command prompt and run the server for you.`;
        } else if (bck.toLowerCase() === "express") {
            instructions += `The Express backend has already been set up.\n\n`;
            instructions += `To start the server, follow these steps:\n`;
            instructions += `1. Navigate to ${folderPath}\n`;
            instructions += `2. Start the server:\n`;
            instructions += `   node server.js\n\n`;
            instructions += `Or, press the "Start" button to automatically open the terminal and run the server for you.`;
        } 
         else if (bck.toLowerCase() === "django") {
        instructions += `The Django backend has already been set up.\n\n`;
        instructions += `To start the server, follow these steps:\n`;
        instructions += `1. Navigate to ${folderPath}\n`;
        instructions += `2. Set up your virtual environment:\n`;
        instructions += `   - Windows: python -m venv venv\n`;
        instructions += `   - Mac/Linux: python3 -m venv venv\n`;
        instructions += `3. Activate the virtual environment:\n`;
        instructions += `   - Windows: venv\\Scripts\\activate\n`;
        instructions += `   - Mac/Linux: source venv/bin/activate\n`;
        instructions += `4. Install the required dependencies:\n`;
        instructions += `   pip install -r requirements.txt\n`;
        instructions += `5. Run the server:\n`;
        instructions += `   python manage.py runserver ${port}\n\n`;
        instructions += `Or, press the "Start" button to automatically open the terminal and run the server for you.`;
    } else {
        instructions += "Backend type not supported yet.";
    }
    
        alert(instructions);
    };
    
    

    return (
        <div className="App">
            <header className="App-header">
                <h2>Create your Backend</h2>
 <input 
                    type='text' 
                    placeholder="Enter Backend App's name"
                    value={backendName}
                    onChange={(e) => setBackendName(e.target.value)}
                    style={{
                        padding: '10px',
                        fontSize: '16px',
                        marginBottom: '10px',
                        marginTop: '15px'
                    }}
                />

                <div style={{
                        padding: '10px',
                        marginBottom: '10px',
                        marginTop: '15px',
                        
                    }}>
                    <label style={{
                        padding: '10px',
                        fontSize: '16px',
                        marginBottom: '10px',
                        marginRight: '15px'
                    }}>
                        <input 
                            type="checkbox" 
                            value="Flask" 
                            checked={selectedBackends.includes("Flask")}
                            onChange={() => handleCheckboxChange("Flask")}
                        /> Flask
                    </label>
                    <label style={{
                        padding: '10px',
                        fontSize: '16px',
                        marginBottom: '10px',
                        marginRight: '15px'
                    }}>
                        <input 
                            type="checkbox" 
                            value="Express" 
                            checked={selectedBackends.includes("Express")}
                            onChange={() => handleCheckboxChange("Express")}
                        /> Express
                    </label>
                    <label style={{
                        padding: '10px',
                        fontSize: '16px',
                        marginBottom: '10px',
                        marginRight: '15px'
                    }}>
                        <input 
                            type="checkbox" 
                            value="Django" 
                            checked={selectedBackends.includes("Django")}
                            onChange={() => handleCheckboxChange("Django")}
                        /> Django
                    </label>
                </div>

                <button
                    onClick={clickButton}
                    style={{
                        padding: "10px",
                        cursor: "pointer",
                        transition: "transform 0.1s ease",
                        marginTop: "15px"
                    }}
                    onMouseEnter={(e) => e.target.style.transform = "scale(1.09)"}
                    onMouseLeave={(e) => e.target.style.transform = "scale(1)"}
                >
                    Create Backend
                </button>

                <h2 style={{
                        padding: '10px',
                        marginBottom: '10px',
                        marginTop: '15px'
                    }}>Backend Port Manager</h2>
                    <div style={{ maxHeight: '300px', maxWidth: '100vw', width: '80%', overflowY: 'auto', border: '1px solid #ccc', borderRadius: '5px' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr>
                            <th>Port</th>
                            <th>App Name</th>
                            <th>Backend Type</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {ports.length > 0 ? ports.map((portInfo, index) => (
                            <tr key={index}>
                                <td>{portInfo.port}</td>
                                <td>{portInfo.app_name}</td>
                                <td>{portInfo.BCK}</td>
                                <td>
                                    <button style={{
                        padding: '5px',
                        marginBottom: '10px',
                        marginTop: '15px',
                        marginRight:"10px"
                    }} onClick={() => handleStart(portInfo.BCK, portInfo.Folder_path)}>Start</button>
                                    <button style={{
                        padding: '5px',
                        marginBottom: '10px',
                        marginTop: '15px',
                        marginRight:"10px"
                    }} onClick={() => handleInstructions(portInfo.Folder_path, portInfo.port, portInfo.app_name, portInfo.BCK, portInfo.unique_number)}>Instructions</button>
                                </td>
                            </tr>
                        )) : (
                            <tr>
                                <td colSpan="5" style={{ textAlign: 'center' }}>No backend instances found.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
                </div>
            </header>
        </div>
    );
}

export default BackendManager;
