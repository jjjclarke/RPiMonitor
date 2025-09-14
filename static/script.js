function updateStats() {
    fetch('/update')
        .then(response => response.json())
        .then(data => {
            // update CPU
            document.getElementById('cpu-meter').style.width = data.cpu_percent + '%';
            document.getElementById('cpu-percent').textContent = data.cpu_percent + '%';
            if (data.cpu_temp) {
                document.getElementById('cpu-temp').textContent = 'Temperature: ' + data.cpu_temp + '°C';
            }

            // update RAM
            document.getElementById('memory-meter').style.width = data.memory.percent + '%';
            document.getElementById('memory-usage').textContent =
                `${data.memory.used}GB / ${data.memory.total}GB (${data.memory.percent}%)`;

            // update disk
            document.getElementById('disk-meter').style.width = data.disk.percent + '%';
            document.getElementById('disk-usage').textContent =
                `${data.disk.used}GB / ${data.disk.total}GB (${data.disk.percent}%)`;

            // update processes
            const processList = document.getElementById('process-list');
            processList.innerHTML = '';
            data.processes.forEach(process => {
                processList.innerHTML += `
                    <tr>
                        <td>${process.pid}</td>
                        <td>${process.name}</td>
                        <td>${process.cpu_percent}</td>
                        <td>${process.memory_percent}</td>
                    </tr>
                `;
            });

            document.getElementById('timestamp').textContent = 'Last updated: ' + data.timestamp;
        })
        .catch(error => console.error('Error fetching updates:', error));
}

// Init
updateStats();

// Update every 10 seconds
setInterval(updateStats, 10000);