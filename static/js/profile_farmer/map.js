/// static/js/profile_farmer/map.js


document.addEventListener("DOMContentLoaded", function() {
    // Initialiser la carte et la géolocalisation
    const defaultLat = 50.8503;
    const defaultLon = 4.3517;
    const map = L.map('map').setView([defaultLat, defaultLon], 13);

    // Ajouter la couche de tuiles OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19,
    }).addTo(map);

    // Ajouter un marqueur initial sur la carte
    const marker = L.marker([defaultLat, defaultLon]).addTo(map)
        .bindPopup("Sélectionnez une adresse")
        .openPopup();

    // Container pour les suggestions d'adresse
    const suggestionsContainer = document.getElementById('suggestions-container');

    // Ajouter un écouteur d'événements sur l'input d'adresse
    document.getElementById('address').addEventListener('input', function(event) {
        const query = event.target.value;
        if (query.length > 2) { // Lancer la recherche après avoir saisi 3 caractères
            searchAddress(query);
        }
    });

    // Fonction de recherche d'adresse
    async function searchAddress(query) {
        suggestionsContainer.innerHTML = ''; // Réinitialiser les suggestions
        if (!query) return;

        try {
            const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&addressdetails=1&limit=5`);
            if (!response.ok) throw new Error("Erreur lors de la récupération des adresses.");
            const data = await response.json();

            if (data.length === 0) {
                suggestionsContainer.innerHTML = '<div class="autocomplete-suggestion">Aucune correspondance trouvée</div>';
                return;
            }

            // Afficher les suggestions d'adresses
            data.forEach(item => {
                const suggestion = document.createElement('div');
                suggestion.classList.add('autocomplete-suggestion');
                suggestion.textContent = item.display_name;
                suggestion.addEventListener('click', () => {
                    // Remplir les champs avec les données de l'adresse sélectionnée
                    document.getElementById('address').value = item.display_name;
                    document.getElementById('latitude').value = item.lat;
                    document.getElementById('longitude').value = item.lon;
                    updateMap(item.lat, item.lon); // Mettre à jour la carte avec la nouvelle adresse
                    suggestionsContainer.innerHTML = ''; // Vider les suggestions
                });
                suggestionsContainer.appendChild(suggestion);
            });
        } catch (error) {
            console.error('Erreur API:', error);
            suggestionsContainer.innerHTML = '<div class="autocomplete-suggestion">Erreur de chargement</div>';
        }
    }

    // Mettre à jour la carte avec la nouvelle adresse
    function updateMap(lat, lon) {
        marker.setLatLng([lat, lon]); // Déplacer le marqueur
        map.setView([lat, lon], 13); // Centrer la carte sur la nouvelle adresse
        marker.bindPopup(`Adresse sélectionnée : ${document.getElementById('address').value}`).openPopup();
    }

});
