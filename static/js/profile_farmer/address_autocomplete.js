// static/js/profile_farmer/address_autocomplete.js

document.addEventListener("DOMContentLoaded", function () {
    let map = L.map('map').setView([50.8503, 4.3517], 13); // Position par défaut à Bruxelles
    let marker = null;

    // Charger la carte
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Ajouter un marqueur si des coordonnées existent déjà
    let lat = document.getElementById('latitude').value;
    let lng = document.getElementById('longitude').value;

    if (lat && lng) {
        marker = L.marker([lat, lng]).addTo(map);
        map.setView([lat, lng], 13);
    }

    // Fonction d'autocomplétion d'adresse avec l'API Nominatim
    document.getElementById('address').addEventListener('input', function () {
        let query = this.value;
        if (query.length > 3) {
            fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&addressdetails=1&limit=5`)
                .then(response => response.json())
                .then(data => {
                    let suggestionsContainer = document.getElementById('suggestions-container');
                    suggestionsContainer.innerHTML = '';
                    suggestionsContainer.style.display = 'block';

                    data.forEach(item => {
                        let suggestion = document.createElement('div');
                        suggestion.classList.add('autocomplete-suggestion');
                        suggestion.textContent = item.display_name;
                        suggestion.addEventListener('click', function () {
                            document.getElementById('address').value = item.display_name;
                            document.getElementById('latitude').value = item.lat;
                            document.getElementById('longitude').value = item.lon;
                            suggestionsContainer.style.display = 'none';

                            // Mettre à jour la carte avec le marqueur
                            if (marker) {
                                map.removeLayer(marker);
                            }
                            marker = L.marker([item.lat, item.lon]).addTo(map);
                            map.setView([item.lat, item.lon], 13);
                        });

                        suggestionsContainer.appendChild(suggestion);
                    });
                })
                .catch(error => {
                    console.error("Erreur lors de la récupération des adresses :", error);
                });
        }
    });

    // Fermer la liste des suggestions si on clique ailleurs
    document.addEventListener("click", function (e) {
        if (!e.target.closest("#suggestions-container") && !e.target.closest("#address")) {
            document.getElementById("suggestions-container").style.display = "none";
        }
    });
});

