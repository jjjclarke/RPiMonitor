from flask import Flask, render_template, jsonify
from datetime import datetime
import psutil
import time

app = Flask(__name__)

stat = (1024.0 ** 3)
process_cpu_cache = {}

def get_cpu_temp():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as temp_file:
            temp = float(temp_file.read()) / 1000.0
        return round(temp, 1)
    except:
        return None

def get_process_info():
    """
    Retrieves information about the top 10 processes sorted by CPU usage.
    This function iterates through all running processes, collects their 
    CPU and memory usage, and returns a list of dictionaries containing 
    the process ID, name, CPU usage percentage, and memory usage percentage. 
    It also maintains a cache to track CPU usage over time for accurate 
    measurements.
    Returns:
        list[dict]: A list of dictionaries, each containing:
            - 'pid' (int): Process ID.
            - 'name' (str): Process name.
            - 'cpu_percent' (float): CPU usage percentage, rounded to 1 decimal place.
            - 'memory_percent' (float): Memory usage percentage, rounded to 1 decimal place.
    Notes:
        - The function sorts the processes by CPU usage in descending order.
        - Only the top 10 processes are returned.
        - Processes that no longer exist or cannot be accessed are skipped.
        - The `process_cpu_cache` global variable is used to store CPU usage 
          data for processes to ensure accurate measurements.
    """
    processes = {p.pid: p for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])}
    processes_info = []

    for proc in processes.values():
        proc.cpu_percent(interval=None)

    time.sleep(0.1)
    
    for proc in processes.values():
        try:
            processes_info.append({
                'pid': proc.pid,
                'name': proc.info['name'],
                'cpu_percent': round(proc.cpu_percent(interval=None), 1),
                'memory_percent': round(proc.info['memory_percent'], 1)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Sort
    processes_info.sort(key=lambda x: x['cpu_percent'], reverse=True)
    
    return processes_info[:10]  # Return top 10 processes

def get_system_info():
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'cpu_temp': get_cpu_temp(),
        'memory': {
            'total': round(psutil.virtual_memory().total / stat, 1),
            'used': round(psutil.virtual_memory().used / stat, 1),
            'percent': psutil.virtual_memory().percent
        },
        'disk': {
            'total': round(psutil.disk_usage('/').total / stat, 1),
            'used': round(psutil.disk_usage('/').used / stat, 1),
            'percent': psutil.disk_usage('/').percent
        },
        'processes': get_process_info(),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

@app.route('/')
def index():
    return render_template('index.html', system_info=get_system_info())

@app.route('/update')
def update():
    return jsonify(get_system_info())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)