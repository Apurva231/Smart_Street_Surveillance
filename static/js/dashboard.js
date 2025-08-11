let lastEmergencyImage = null;

function updateSensorData() {
    fetch('/get_data')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error(data.error);
                document.querySelectorAll('.sensor p').forEach(p => p.innerHTML = '<span class="error">N/A</span>');
            } else {
                const sensorData = data.sensor_data;

                document.querySelector('#temperature p').textContent = sensorData.temperature !== null ? sensorData.temperature + ' °C' : 'N/A';
                document.querySelector('#humidity p').textContent = sensorData.humidity !== null ? sensorData.humidity + ' %' : 'N/A';
                document.querySelector('#co2 p').textContent = sensorData.co2 !== null ? sensorData.co2 + ' ppm' : 'N/A';
                document.querySelector('#ldr p').textContent = sensorData.ldr !== null ? sensorData.co2 : 'N/A';
                document.querySelector('#motion p').textContent = sensorData.motion !== null ? (sensorData.motion ? 'Detected' : 'Not Detected') : 'N/A';
                document.querySelector('#emergency p').textContent = sensorData.emergency !== null ? sensorData.emergency : 'N/A';

                // 📸 Capture and send image with location if emergency is detected
                if (sensorData.emergency === 1 && sensorData.image_path && sensorData.image_path !== lastEmergencyImage) {
                    lastEmergencyImage = sensorData.image_path;

                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(
                            position => {
                                const lat = position.coords.latitude;
                                const lon = position.coords.longitude;
                                const image_url = sensorData.image_path;

                                fetch('/emergency', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ lat, lon, image_url })
                                })
                                    .then(res => res.json())
                                    .then(res => {
                                        if (res.status === "success") {
                                            document.getElementById('status').textContent = "📍 Emergency reported with location.";
                                        } else {
                                            document.getElementById('status').textContent = "❌ Failed to report location.";
                                        }
                                    });
                            },
                            err => {
                                document.getElementById('status').textContent = "⚠️ Location access denied.";
                                console.error(err);
                            }
                        );
                    } else {
                        document.getElementById('status').textContent = "❌ Geolocation not supported.";
                    }
                }
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            document.querySelectorAll('.sensor p').forEach(p => p.innerHTML = '<span class="error">N/A</span>');
        });
}

// Initial load and polling
updateSensorData();
setInterval(updateSensorData, 1000);