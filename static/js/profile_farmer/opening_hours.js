//static/js/profile_farmer/opening_hours.js




document.addEventListener("DOMContentLoaded", function () {
    // Fonction pour activer ou désactiver les champs horaires selon l'état "fermé"
    document.querySelectorAll(".is-closed").forEach(checkbox => {
        checkbox.addEventListener("change", function () {
            const row = this.closest("tr");
            const openingTimeInput = row.querySelector(".opening-time");
            const closingTimeInput = row.querySelector(".closing-time");

            if (this.checked) {
                openingTimeInput.disabled = true;
                closingTimeInput.disabled = true;
            } else {
                openingTimeInput.disabled = false;
                closingTimeInput.disabled = false;
            }
        });
    });

    // Fonction pour sauvegarder les horaires via AJAX
    const saveButton = document.getElementById("saveOpeningHours");
    if (saveButton) {
        saveButton.addEventListener("click", function () {
            const rows = document.querySelectorAll("#openingHoursTable tr");
            const data = [];

            rows.forEach(row => {
                const day = row.dataset.day || 'Inconnu'; // Valeur par défaut
                const openingTimeInput = row.querySelector(".opening-time");
                const closingTimeInput = row.querySelector(".closing-time");

                if (!openingTimeInput || !closingTimeInput) {
                    console.error("Impossible de trouver les champs horaires pour le jour", day);
                    return; // Ignorer cette ligne
                }

                const openingTime = openingTimeInput.value || null;
                const closingTime = closingTimeInput.value || null;
                const isClosed = row.querySelector(".is-closed").checked;

                data.push({
                    day_of_week: day,
                    opening_time: isClosed ? null : openingTime,
                    closing_time: isClosed ? null : closingTime,
                    is_closed: isClosed
                });
            });

            // Affichage pour débogage
            console.log("Données à envoyer:", data);


            fetch(saveOpeningHoursUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: JSON.stringify({ opening_hours: data })
            })
            .then(response => {
                if (response.ok) {
                    alert("Horaires enregistrés avec succès !");
                    window.location.reload(); // Recharger la page pour voir les mises à jour
                } else {
                    alert("Erreur lors de l'enregistrement des horaires.");
                }
            })
            .catch(error => {
                console.error("Erreur :", error);
                alert("Erreur lors de la connexion au serveur.");
            });
        });
    }
});
