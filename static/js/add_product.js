// static/js/add_product.js


// Fonction pour initialiser la prévisualisation du produit
function initPreview() {
    const updatePreviewButton = document.getElementById('updatePreviewButton');
    if (updatePreviewButton) {
        updatePreviewButton.addEventListener('click', updateProductPreview);
    }

    // Ajout d'un écouteur pour l'input de fichier
    const imageInput = document.getElementById('id_image');
    if (imageInput) {
        imageInput.addEventListener('change', updateProductPreview);
    }

    // Ajout d'un écouteur pour l'URL de l'image
    const imageUrlInput = document.getElementById('id_image_url');
    if (imageUrlInput) {
        imageUrlInput.addEventListener('input', updateProductPreview);
    }
}

// Fonction pour mettre à jour la prévisualisation du produit
function updateProductPreview() {
    // Récupérer les éléments du formulaire
    const name = document.getElementById('id_name').value;
    const description = document.getElementById('id_description').value;
    const price = document.getElementById('id_price').value;
    const category = document.getElementById('id_category').value;
    const stock = document.getElementById('id_stock').value;
    const imageUrl = document.getElementById('id_image_url').value;
    const imageFile = document.getElementById('id_image').files[0];

    // Mettre à jour les éléments de prévisualisation
    updatePreviewTextContent('previewName', name);
    updatePreviewTextContent('previewDescription', description);
    updatePreviewTextContent('previewPrice', `${price} €`);
    updatePreviewTextContent('previewCategory', category);
    updatePreviewTextContent('previewStock', stock);

    // Mise à jour de l'image de prévisualisation
    const previewImageElement = document.getElementById('previewImage');
    if (imageFile) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImageElement.src = e.target.result;
            previewImageElement.style.display = 'block'; // Afficher l'image
        };
        reader.readAsDataURL(imageFile);  // Lire l'image comme URL de données
    } else if (imageUrl) {
        previewImageElement.src = imageUrl;
        previewImageElement.style.display = 'block'; // Afficher l'image si l'URL est fournie
    } else {
        previewImageElement.style.display = 'none'; // Cacher l'image si aucune image ou URL
    }
}

// Fonction générique pour mettre à jour le texte des éléments de prévisualisation
function updatePreviewTextContent(elementId, content) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = content || 'Aucune information fournie'; // Gérer les valeurs vides
    }
}

// Fonction pour initialiser le formulaire et les actions sur les boutons
function initFormActions() {
    const form = document.getElementById('productForm');
    if (form) {
        form.addEventListener('submit', function(event) {
            // Si une erreur de formulaire, annuler la soumission (par exemple si non validé)
            if (form.checkValidity() === false) {
                event.preventDefault();  // Empêcher la soumission si le formulaire est invalide
                displayFormError('Veuillez corriger les erreurs dans le formulaire.');
            }
        });
    }
}

// Fonction pour afficher les erreurs du formulaire
function displayFormError(message) {
    const errorContainer = document.querySelector('.alert');
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    }
}

// Initialiser toutes les actions du formulaire et la prévisualisation
document.addEventListener('DOMContentLoaded', function () {
    initPreview();
    initFormActions();
});
