import os
import re
import socket
import subprocess


def get_ipv4():
    host_name = socket.gethostname()
    return socket.gethostbyname(host_name)


def server_running(port=6379):
    with os.popen(f"netstat -ano | findstr {port}") as r:
        pids = set([i.strip() for i in re.findall('LISTENING(.*)', r.read())])

    return True if pids else False


def start_cmd(command, close=True):
    if close:
        process = subprocess.Popen(f'start cmd /c {command}', shell=True)
    else:
        process = subprocess.Popen(f'start cmd /k {command}', shell=True)
    return process.pid


def start_python_in_background(path, close=True):
    return start_cmd(command=f'python {path}', close=close)


def close_program_by_port(port):
    with os.popen(f"netstat -ano | findstr {port}") as r:
        pids = set([i.strip() for i in re.findall('LISTENING(.*?)\n', r.read())])

    for pid in pids:
        os.system(f"taskkill /PID {pid.strip()} /T /F")
