const map = L.map('map').setView([19.076, 72.8777], 12); // Default center: Mumbai

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

fetch('/get_emergencies')
    .then(response => response.json())
    .then(data => {
        if (!Array.isArray(data)) {
            console.error("Invalid emergency data:", data);
            return;
        }

        let addedMarker = false;

        data.forEach(entry => {
            let { latitude, longitude, image_url, timestamp } = entry;

            // Convert to float and validate
            latitude = parseFloat(latitude);
            longitude = parseFloat(longitude);

            const isValidCoord = !isNaN(latitude) && !isNaN(longitude) &&
                latitude >= -90 && latitude <= 90 &&
                longitude >= -180 && longitude <= 180;

            if (isValidCoord) {
                const popupContent = `
                    <strong>🚨 Emergency Detected</strong><br>
                    <em>${timestamp || ''}</em><br>
                    ${image_url ? `<img src="/static/${image_url}" class="popup-img">` : ''}
                `;

                L.marker([latitude, longitude])
                    .addTo(map)
                    .bindPopup(popupContent);

                if (!addedMarker) {
                    map.setView([latitude, longitude], 14); // Zoom in on the first marker
                    addedMarker = true;
                }
            }
        });
    })
    .catch(error => {
        console.error("Failed to fetch emergencies:", error);
    });
