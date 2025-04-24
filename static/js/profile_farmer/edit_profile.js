//static/js/profile_farmer/edit_profile.js

document.addEventListener('DOMContentLoaded', function () {
    const map = L.map('map').setView([48.8566, 2.3522], 12);

    // Ajout des tuiles OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);

    let marker;

    const addressInput = document.getElementById('address-input');
    const addressSuggestions = document.getElementById('address-suggestions');
    const latitudeInput = document.getElementById('id_latitude');
    const longitudeInput = document.getElementById('id_longitude');

    // Gestion des suggestions d'adresse
    addressInput.addEventListener('input', function () {
        const query = this.value;

        if (query.length > 3) {
            fetch(`https://nominatim.openstreetmap.org/search?q=${query}&format=json&addressdetails=1`)
                .then(response => response.json())
                .then(data => {
                    addressSuggestions.innerHTML = '';
                    data.forEach(item => {
                        const div = document.createElement('div');
                        div.classList.add('address-suggestion-item');
                        div.textContent = item.display_name;
                        div.addEventListener('click', function () {
                            addressInput.value = item.display_name;
                            addressSuggestions.innerHTML = '';

                            const lat = parseFloat(item.lat);
                            const lon = parseFloat(item.lon);

                            map.setView([lat, lon], 14);

                            if (marker) {
                                map.removeLayer(marker);
                            }

                            marker = L.marker([lat, lon]).addTo(map);

                            latitudeInput.value = lat;
                            longitudeInput.value = lon;
                        });
                        addressSuggestions.appendChild(div);
                    });
                })
                .catch(error => console.error('Erreur lors de la recherche d\'adresse :', error));
        }
    });
});
