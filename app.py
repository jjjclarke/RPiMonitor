from flask import Flask, render_template, jsonify
from datetime import datetime
import psutil
import time

app = Flask(__name__)

stat = (1024.0 ** 3)
process_cpu_cache = {}

# Reads temperature from a file which is specific to the Pi
def get_cpu_temp():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as temp_file:
            temp = float(temp_file.read()) / 1000.0
        return round(temp, 1)
    except:
        return None

def get_process_info():
    global process_cpu_cache
    current_time = time.time()
    processes_info = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            proc_info = proc.info
            pid = proc_info['pid']
            
            # calculate CPU percent
            if pid in process_cpu_cache:
                cpu_percent = proc.cpu_percent() 
                time.sleep(0.1)     # delay to ensure measurement
                cpu_percent = proc.cpu_percent()  # get the actual measurement
            else:
                process_cpu_cache[pid] = {
                    'cpu_percent': proc.cpu_percent(),
                    'time': current_time
                }
                cpu_percent = 0  # Init call
            
            mem_percent = proc_info['memory_percent']
            
            processes_info.append({
                'pid': pid,
                'name': proc_info['name'],
                # Convert to float otherwise thing would not work ???
                'cpu_percent': round(float(cpu_percent), 1),
                'memory_percent': round(float(mem_percent), 1)
            })
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    # Sort
    processes_info.sort(key=lambda x: x['cpu_percent'], reverse=True)
    
    # Clean
    current_pids = set(p['pid'] for p in processes_info)
    process_cpu_cache = {pid: data for pid, data in process_cpu_cache.items() 
                        if pid in current_pids}
    
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