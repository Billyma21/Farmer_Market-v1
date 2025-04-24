document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('farmer-profile-form');

    form.addEventListener('submit', function (e) {
        e.preventDefault(); // Empêche l'envoi standard du formulaire

        const formData = new FormData(this);

        fetch("{% url 'edit_profile' %}", {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
            .then(response => {
                if (response.ok) {
                    alert('Profil mis à jour avec succès!');
                    window.location.href = "{% url 'farmer_dashboard' %}"; // Redirection après succès
                } else {
                    alert('Erreur lors de l\'enregistrement du profil.');
                }
            })
            .catch(error => {
                console.error('Erreur lors de l\'envoi du formulaire:', error);
                alert('Erreur de connexion.');
            });
    });
});
