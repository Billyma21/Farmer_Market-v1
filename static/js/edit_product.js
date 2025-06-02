// // static/js/edit_product.js

// static/js/edit_product.js

// Fonction pour mettre à jour la prévisualisation du produit
function updatePreview() {
    const name = document.querySelector('#id_name').value;
    const description = document.querySelector('#id_description').value;
    const price = document.querySelector('#id_price').value;
    const category = document.querySelector('#id_category option:checked') ? document.querySelector('#id_category option:checked').text : '';
    const stock = document.querySelector('#id_stock').value;
    const imageFile = document.querySelector('#image').files[0];
    const imageUrl = document.querySelector('#image_url').value;

    // Mise à jour des champs de texte dans la prévisualisation
    document.querySelector('#previewName').textContent = name || 'N/A';
    document.querySelector('#previewDescription').textContent = description || 'N/A';
    document.querySelector('#previewPrice').textContent = price ? `${price} €` : 'N/A';
    document.querySelector('#previewCategory').textContent = category || 'N/A';
    document.querySelector('#previewStock').textContent = stock || 'N/A';

    // Gestion de la prévisualisation de l'image
    const previewImage = document.querySelector('#previewImage');
    if (imageFile) {
        const reader = new FileReader();
        reader.onload = function (e) {
            previewImage.src = e.target.result; // Affiche l'image locale
        };
        reader.readAsDataURL(imageFile);
    } else if (imageUrl) {
        previewImage.src = imageUrl; // Affiche l'image externe
    } else {
        previewImage.src = '/static/images/default-image.jpg'; // Image par défaut
    }
}

// Ajout d'événements pour la mise à jour en temps réel de la prévisualisation
document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#image').addEventListener('change', updatePreview);
    document.querySelector('#image_url').addEventListener('input', updatePreview);
});


// // static/js/edit_product.js

// function updatePreview() {
//     const name = document.querySelector('#id_name').value;
//     const description = document.querySelector('#id_description').value;
//     const price = document.querySelector('#id_price').value;
//     const category = document.querySelector('#id_category option:checked').text;
//     const stock = document.querySelector('#id_stock').value;
//     const imageFile = document.querySelector('#image').files[0];
//     const imageUrl = document.querySelector('#image_url').value;

//     // Mise à jour des champs de prévisualisation
//     document.querySelector('#previewName').textContent = name || 'N/A';
//     document.querySelector('#previewDescription').textContent = description || 'N/A';
//     document.querySelector('#previewPrice').textContent = price ? `${price} €` : 'N/A';
//     document.querySelector('#previewCategory').textContent = category || 'N/A';
//     document.querySelector('#previewStock').textContent = stock || 'N/A';

//     // Gestion de l'image
//     const previewImage = document.querySelector('#previewImage');
//     if (imageFile) {
//         const reader = new FileReader();
//         reader.onload = function (e) {
//             previewImage.src = e.target.result; // Affiche l'image locale
//         };
//         reader.readAsDataURL(imageFile);
//     } else if (imageUrl) {
//         previewImage.src = imageUrl; // Affiche l'image externe
//     } else {
//         previewImage.src = '/static/images/default-image.jpg'; // Image par défaut
//     }

    
// }
