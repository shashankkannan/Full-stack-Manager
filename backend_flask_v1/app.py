from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import os
import json
import threading
import time
import uuid

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return jsonify({'message': 'Welcome to Project Manager! Build and manage your apps with ease here!'})


@app.route('/about')
def about():
    return jsonify({'message': 'Welcome to the About page. This is a message from Flask!'})


PROJECTS_DIR = os.path.join(os.getcwd(), "projects_child")
PROJECTS_DIR_BCK = os.path.join(os.getcwd(), "projects_bck_child")
PORTS_FILE = os.path.join(os.getcwd(), "ports.json")
PORTS_FILE_BCK = os.path.join(os.getcwd(), "bck_ports.json")


# Function to get the next available port
def get_next_available_port(app_name):
    if not os.path.exists(PORTS_FILE):
        with open(PORTS_FILE, "w") as f:
            json.dump({"20000": {"app_name": "None", "State": "stopped"}}, f,
                      indent=4)  # Store keys as strings for JSON compatibility

    with open(PORTS_FILE, "r") as f:
        ports = json.load(f)

    # Convert keys to integers and find the highest used port
    used_ports = {int(k): v for k, v in ports.items()}
    last_used_port = max(used_ports.keys(), default=20000)
    next_port = last_used_port + 1

    # Add the new port to the file with app_name and initial state
    ports[str(next_port)] = {"app_name": app_name, "State": "stopped"}  # Store app_name and State

    # Save the updated ports to the file
    with open(PORTS_FILE, "w") as f:
        json.dump(ports, f, indent=4)

    return next_port  # Return as an integer


@app.route('/create-app', methods=['POST'])
def create_app():
    data = request.get_json()
    app_name = data.get("app_name", "").strip()

    if not app_name:
        return jsonify({"error": "No app name!"}), 400

    if not os.path.exists(PROJECTS_DIR):
        os.makedirs(PROJECTS_DIR)  # Ensure projects_child directory exists

    app_path = os.path.join(PROJECTS_DIR, app_name)
    print(app_path)
    if os.path.exists(app_path):
        return jsonify({"error": f"App '{app_name}' already exists!"}), 400
    elif not os.path.exists(app_path):
        os.makedirs(app_path)  # Create the app directory

    try:
        # Get the next available port
        assigned_port = get_next_available_port(app_name)

        commands = [
            f"cd {app_path} && set CI=true && npx create-react-app@latest {app_name}",  # Create the app
            f"cd {app_path}/{app_name} && npm install ajv@latest ajv-keywords@latest",  # Install ajv and ajv-keywords
            f"cd {app_path}/{app_name} && npm install react-router-dom",  # Install react-router-dom
            f"cd {app_path}/{app_name} && npm install axios",  # Install axios
            f"cd {app_path}/{app_name} && npm install cross-env --save-dev",  # Install cross-env
            f"cd {app_path}/{app_name} && npm install react-router-dom"  # Install react-router-dom (again)
        ]

        # Run each command in sequence
        for command in commands:
            try:
                process = subprocess.run(command, shell=True, check=True, text=True)
                print(f"Command succeeded: {command}")
            except subprocess.CalledProcessError as e:
                return jsonify({"error": f"Command failed: {command}. Error: {str(e)}"}), 500

        # Modify package.json to set the assigned port
        app_direc = os.path.join(app_path, app_name)
        package_json_path = os.path.join(app_direc, "package.json")

        with open(package_json_path, "r") as f:
            package_data = json.load(f)

        package_data["scripts"]["start"] = f"cross-env PORT={assigned_port} react-scripts start"

        with open(package_json_path, "w") as f:
            json.dump(package_data, f, indent=2)

        # Start the React app with the assigned port
        # subprocess.Popen(f"cd {app_direc} && npm start", shell=True, cwd=PROJECTS_DIR)

        return jsonify({"message": f"React app '{app_name}' created and running on port {assigned_port}!"})

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Failed to create app: {str(e)}"}), 500


def get_pid_of_process_on_port(port):
    try:
        # For Windows
        pid = os.popen(f"netstat -ano | findstr :{port}").read()

        # Check if the command returned any output
        if pid:
            pid = pid.split()[-1]  # Extract the PID from the output
            return pid.strip()
        else:
            return None  # No process found on the port
    except Exception as e:
        # If any error occurs during the process
        print(f"Error: {e}")
        return None


def kill_process(pid):
    try:
        # Using 'runas' to elevate the taskkill command to run as an administrator
        print(f"Attempting to kill process with PID {pid}")

        # Use 'runas' to execute with elevated privileges
        result = subprocess.run(f"runas /user:Administrator \"taskkill /PID {pid} /F\"", shell=True,
                                capture_output=True, text=True)

        # Check if taskkill was successful
        if result.returncode == 0:
            print(f"SUCCESS: The process with PID {pid} has been terminated.")
            return True
        else:
            print(f"FAILURE: Could not terminate the process. Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error killing process: {e}")
        return False


@app.route('/stop_process', methods=['POST'])
def stop_process():
    port = request.json.get('port')

    if not port:
        return jsonify({"error": "Port is required."}), 400

    pid = get_pid_of_process_on_port(port)

    if pid and pid != "0":  # Ensure valid PID is found
        success = kill_process(pid)
        if success:
            return jsonify({"message": f"Process on port {port} (PID: {pid}) has been stopped."}), 200
        else:
            return jsonify({"error": f"Failed to kill process with PID {pid}."}), 500
    else:
        return jsonify({"message": f"No process found on port {port}."}), 404

@app.route('/get-ports', methods=['GET'])
def get_ports():
    try:
        if not os.path.exists(PORTS_FILE):
            return jsonify({"error": "No ports data found!"}), 404

        with open(PORTS_FILE, "r") as f:
            ports = json.load(f)

        # Prepare the list of ports with app names and states
        ports_info = [
            {"port": port, "app_name": info["app_name"], "state": info["State"]}
            for port, info in ports.items()
        ]

        return jsonify({"ports": ports_info})

    except Exception as e:
        return jsonify({"error": f"Error fetching ports: {str(e)}"}), 500


@app.route('/start-app', methods=['POST'])
def start_app():
    data = request.json
    app_name = data.get("app_name")
    app_port = str(data.get("app_port"))
    print(app_name)

    if not app_name or not app_port:
        return jsonify({"error": "App name and port are required"}), 400

    app_path = os.path.join(PROJECTS_DIR, app_name, app_name)  # projects_child/app_name/app_name/

    if not os.path.exists(app_path):
        return jsonify({"error": f"App directory {app_path} does not exist"}), 400

    try:
        if os.name == "nt":  # Windows
            subprocess.Popen(
                f'start cmd /k "cd /d {app_path} && npm start"', shell=True
            )
        else:  # macOS / Linux
            subprocess.Popen(
                ['gnome-terminal', '--', 'bash', '-c', f'cd "{app_path}" && npm start; exec bash']
            )

        if os.path.exists(PORTS_FILE):
            with open(PORTS_FILE, "r") as f:
                ports = json.load(f)

            # Check if the port exists and update the state
            if app_port in ports and ports[app_port]["app_name"] == app_name:
                ports[app_port]["State"] = "running"  # Change state to running

                # Save the updated state back to ports.json
                with open(PORTS_FILE, "w") as f:
                    json.dump(ports, f, indent=4)

                return jsonify({"message": f"App '{app_name}' started and state updated to 'running'!"}), 200
            else:
                return jsonify({"error": "Port entry not found or app name mismatch"}), 400
        else:
            return jsonify({"error": "Ports file not found!"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def monitor_ports():
    """ Continuously checks if React apps are running and updates their states in ports.json """
    while True:
        try:
            if not os.path.exists(PORTS_FILE):
                print("No ports.json file found!")
                time.sleep(5)
                continue  # Skip this iteration and wait

            with open(PORTS_FILE, "r") as f:
                ports = json.load(f)

            for port, info in ports.items():
                app_name = info["app_name"]
                current_state = info["State"]
                pid = get_pid_of_process_on_port(port)
                # print(pid, ": ", app_name, ": ", port, ": ", current_state)
                # If no process is running on the port, update the state to "stopped"
                if (pid is None or pid == "0") and current_state == "running":
                    print(f"App '{app_name}' on port {port} has stopped.")
                    ports[port]["State"] = "stopped"
                elif pid is not None and pid != 0:
                    ports[port]["State"] = "running"

            # Save the updated port states back to ports.json
            with open(PORTS_FILE, "w") as f:
                json.dump(ports, f, indent=4)

        except Exception as e:
            print(f"Error monitoring ports: {e}")

        time.sleep(5)  # Wait for 10 seconds before checking again


@app.route('/open-in-vscode', methods=['POST'])
def open_in_vscode():
    try:
        data = request.json
        app_name = data.get("app_name")
        print(app_name)

        if not app_name:
            return jsonify({"error": "App name is required"}), 400

        # Construct the full path to the project
        app_path = os.path.join(PROJECTS_DIR, app_name, app_name)
        print(f"appp pathsss: {app_path}")

        # Check if the path exists
        if not os.path.exists(app_path):
            print(f"Path does not exist : {app_path}")
            return jsonify({"error": f"Path '{app_path}' does not exist"}), 404
        formatted_path = f'"{app_path}"'  # Ensures spaces are handled correctly

        # Open VS Code at the specified path
        subprocess.Popen(f'code {formatted_path}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return jsonify({"message": f"Opening {app_name} in VS Code"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------ Back-end code-------------------------------------------------------------------


def get_next_available_port_bck(app_name, bck):
    if not os.path.exists(PORTS_FILE_BCK):
        with open(PORTS_FILE_BCK, "w") as f:
            json.dump({"9600": {"app_name": "None", "unique_number": "1234yuiipo", "State": "stopped", "BCK": "bck",
                                "Folder_path": "proj"}},
                      f, indent=6)

    with open(PORTS_FILE_BCK, "r") as f:
        ports = json.load(f)

    # Convert port keys to integers
    used_ports = {int(k): v for k, v in ports.items()}
    last_used_port = max(used_ports.keys(), default=9600)
    next_port = last_used_port + 1

    # Generate a unique identifier
    unique_id = str(uuid.uuid4())[:8]
    apn = app_name + unique_id
    fp = os.path.join(PROJECTS_DIR_BCK, apn)
    # Assign new entry
    ports[str(next_port)] = {"app_name": app_name, "unique_number": unique_id, "State": "stopped", "BCK": bck,
                             "Folder_path": fp}

    # Save updated data
    with open(PORTS_FILE_BCK, "w") as f:
        json.dump(ports, f, indent=4)

    return next_port, unique_id  # Return assigned port and unique identifier


@app.route("/choice_backend", methods=['GET'])
def choice_backend():
    backend = request.args.get('backend', '')  # Get as string
    backend_list = backend.split(",") if backend else []
    app_name = request.args.get("backend_name", "").strip()

    if not os.path.exists(PROJECTS_DIR_BCK):
        os.makedirs(PROJECTS_DIR_BCK)

    response_data = []

    for bck in backend_list:
        bck = bck.strip()
        if bck in ["Flask", "Express", "Django"]:
            port, unique_id = get_next_available_port_bck(app_name, bck)
            print(f"{app_name} ({unique_id}) will run {bck} backend tasks on port {port}")
            apn = app_name + unique_id
            fp = os.path.join(PROJECTS_DIR_BCK, apn)
            response_data.append(
                {"backend": bck, "app_name": app_name, "unique_id": unique_id, "port": port, "Folder_name": fp})
            app_p = os.path.join(PROJECTS_DIR_BCK, apn)
            if not os.path.exists(app_p):
                os.makedirs(app_p)
            if bck == "Flask":
                setup_flask_backend(app_p, port)
                print(f"Create Flask backend for {app_p}")
            elif bck == "Express":
                setup_express_backend(app_p, port)
                print(f"Create Express backend for {app_p}")
            elif bck == "Django":
                setup_django_backend(app_p, port)
                print(f"Create Django backend for {app_p}")

    return jsonify({"message": f"Backends assigned: {backend_list}", "details": response_data})


def setup_django_backend(app_p, port):
    """Sets up a Django backend in a new command prompt window."""
    try:
        # Ensure the project directory exists
        if not os.path.exists(app_p):
            os.makedirs(app_p)

        # Virtual environment activation command based on OS
        activate_script = "venv\\Scripts\\activate && " if os.name == "nt" else "source venv/bin/activate && "

        # Commands to set up Django
        commands = [
            f"cd {app_p}",
            "python -m venv venv",
            f"{activate_script}pip install django",
            f"{activate_script}pip install djangorestframework",
            f"{activate_script}pip install django-cors-headers",
            f"{activate_script}django-admin startproject backend .",
            f"{activate_script}python manage.py startapp api",
        ]

        # Windows: Open a new Command Prompt and run the commands
        if os.name == "nt":
            subprocess.Popen(["cmd.exe", "/k", " && ".join(commands)], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", " ; ".join(commands) + "; exec bash"])

        time.sleep(5)  # Give some time for setup to complete before modifying files

        # Modify backend/settings.py
        settings_path = os.path.join(app_p, "backend", "settings.py")
        with open(settings_path, "r") as file:
            settings_content = file.readlines()

        updated_settings = []
        for line in settings_content:
            updated_settings.append(line)
            if "INSTALLED_APPS = [" in line:
                updated_settings.append("    'api',\n    'corsheaders',\n")
            if "MIDDLEWARE = [" in line:
                updated_settings.append("    'corsheaders.middleware.CorsMiddleware',\n")
        updated_settings.append("\nCORS_ALLOW_ALL_ORIGINS = True\n")

        with open(settings_path, "w") as file:
            file.writelines(updated_settings)

        # Create api/urls.py
        api_urls_path = os.path.join(app_p, "api", "urls.py")
        with open(api_urls_path, "w") as file:
            file.write("""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
]
""")

        # Modify backend/urls.py
        backend_urls_path = os.path.join(app_p, "backend", "urls.py")
        with open(backend_urls_path, "r") as file:
            urls_content = file.readlines()

        updated_urls = []
        for line in urls_content:
            if "from django.urls import path" in line:
                updated_urls.append("from django.urls import path, include\n")
            updated_urls.append(line)
            if "urlpatterns = [" in line:
                updated_urls.append("    path('', include('api.urls')),)\n")

        with open(backend_urls_path, "w") as file:
            file.writelines(updated_urls)

        # Create api/views.py
        api_views_path = os.path.join(app_p, "api", "views.py")
        with open(api_views_path, "w") as file:
            file.write("""
from django.shortcuts import render
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Hello from Django Backend!"})

def about(request):
    return JsonResponse({"message": "Welcome to the About Page (Django)"})
""")

        # Run the Django server in a new terminal
        runserver_command = f"cd {app_p} && {activate_script}python manage.py runserver {port}"
        if os.name == "nt":
            subprocess.Popen(["cmd.exe", "/k", runserver_command], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", runserver_command + "; exec bash"])

        print(f"Django backend setup completed at {app_p}, running on port {port}")

    except Exception as e:
        print(f"Error setting up Django backend: {e}")


def setup_flask_backend(app_p, port):
    """ Sets up a Flask backend in a new command prompt window. """
    try:
        # Ensure the project directory exists
        if not os.path.exists(app_p):
            os.makedirs(app_p)

        # Virtual environment activation command based on OS
        activate_script = "venv\\Scripts\\activate && " if os.name == "nt" else "source venv/bin/activate && "

        # Create `app.py` with Flask boilerplate code
        app_py_content = f"""from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({{'message': 'Hello from Flask with Axios!'}})

@app.route('/about')
def about():
    return jsonify({{'message': 'Hello from Flask in about with Axios!'}})

if __name__ == '__main__':
    app.run(debug=True, port={port})
"""
        with open(os.path.join(app_p, "app.py"), "w") as f:
            f.write(app_py_content)

        # Commands to run in the new terminal
        commands = [
            f"cd /d {app_p}" if os.name == "nt" else f"cd {app_p}",
            "python -m venv venv",
            f"{activate_script}pip install flask-cors",
        ]

        # Windows: Open a new Command Prompt and run the commands
        if os.name == "nt":
            subprocess.Popen(["cmd.exe", "/k", " && ".join(commands)], creationflags=subprocess.CREATE_NEW_CONSOLE)
        # Mac/Linux: Open a new Terminal window
        else:
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", " ; ".join(commands) + "; exec bash"])

        print(f"Flask backend setup started at {app_p}, running on port {port}")

    except Exception as e:
        print(f"Error setting up Flask backend: {e}")


def setup_express_backend(app_p, port):
    """Sets up an Express.js backend in a new command prompt window."""
    try:
        # Create `server.js` with Express boilerplate code
        server_js_content = f'''const express = require("express");
const cors = require("cors");

const app = express();
const PORT = {port};

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {{
  res.json({{ message: "Hello from Express Backend!" }});
}});

app.get("/about", (req, res) => {{
  res.json({{ message: "Welcome to the About Page(Express)" }});
}});

app.listen(PORT, () => {{
  console.log(`Express server running on http://localhost:{port}`);
}});
'''
        # Write the server.js file in the specified app directory
        with open(os.path.join(app_p, "server.js"), "w") as f:
            f.write(server_js_content)

        # Windows: Open CMD and run Node.js setup
        commands = [
            f"cd /d {app_p}",
            "npm init -y",
            "npm install express cors"
        ]
        subprocess.Popen(["cmd.exe", "/k", " && ".join(commands)], creationflags=subprocess.CREATE_NEW_CONSOLE)

        print(f"Express backend setup started at {app_p}, running on port {port}")

    except Exception as e:
        print(f"Error setting up Express backend: {e}")


@app.route('/get-ports-bck', methods=['GET'])
def get_ports_bck():
    try:
        if not os.path.exists(PORTS_FILE_BCK):
            return jsonify({"error": "No ports data found!"}), 404

        with open(PORTS_FILE_BCK, "r") as f:
            ports = json.load(f)

        # Prepare the list of ports with app names and states
        ports_info = [
            {"port": port, "app_name": info["app_name"], "Folder_path": info["Folder_path"],
             "unique_number": info["unique_number"], "BCK": info["BCK"]}
            for port, info in ports.items()
        ]

        return jsonify({"ports": ports_info})

    except Exception as e:
        return jsonify({"error": f"Error fetching ports: {str(e)}"}), 500


@app.route('/start-backend-flask', methods=['POST'])
def start_backend_flask():
    data = request.json
    folder_path = data.get('folder_path')

    if not folder_path or not os.path.exists(folder_path):
        return jsonify({"error": "Invalid folder path"}), 400

    try:
        # Check if PowerShell exists
        powershell_path = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
        if os.path.exists(powershell_path):
            # Open PowerShell in the folder
            subprocess.Popen(f'start powershell -NoExit -Command "cd \'{folder_path}\'"', shell=True)
            return jsonify({
                "message": f"PowerShell opened at {folder_path}. Run 'venv\\Scripts\\activate' and 'python app.py' manually."}), 200
        else:
            # Fallback to CMD if PowerShell is not available
            subprocess.Popen(f'start cmd /K cd /d "{folder_path}"', shell=True)
            return jsonify({
                "message": f"CMD opened at {folder_path}. Run 'venv\\Scripts\\activate' and 'python app.py' manually."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/start-backend-express', methods=['POST'])
def start_backend_express():
    data = request.json
    folder_path = data.get('folder_path')

    if not folder_path or not os.path.exists(folder_path):
        return jsonify({"error": "Invalid folder path"}), 400

    try:
        powershell_path = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
        if os.path.exists(powershell_path):
            # Open PowerShell in the folder
            subprocess.Popen(f'start powershell -NoExit -Command \"cd \'{folder_path}\'"', shell=True)
            return jsonify({
                "message": f"PowerShell opened at {folder_path}. Run 'node server.js' manually."
            }), 200
        else:
            # Fallback to CMD
            subprocess.Popen(f'start powershell -NoExit -Command "cd \'{folder_path}\'"', shell=True)
            return jsonify({
                "message": f"CMD opened at {folder_path}. Run 'node server.js' manually."
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/start-backend-django', methods=['POST'])
def start_backend_django():
    data = request.json
    folder_path = data.get('folder_path')

    if not folder_path or not os.path.exists(folder_path):
        return jsonify({"error": "Invalid folder path"}), 400

    try:
        powershell_path = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
        activate_script = "venv\\Scripts\\activate && " if os.name == "nt" else "source venv/bin/activate && "

        if os.path.exists(powershell_path):
            subprocess.Popen(f'start powershell -NoExit -Command \"cd \'{folder_path}\'"', shell=True)
            return jsonify({
                               "message": f"Run python manage.py runserver for Django backend to start at {folder_path}."}), 200
        else:
            return jsonify({"message": f"Django backend started at {folder_path} on port."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Start the background thread for monitoring ports
    monitor_thread = threading.Thread(target=monitor_ports, daemon=True)
    monitor_thread.start()
    app.run(debug=True, port=5000)
