Dropzone.autoDiscover = false;

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    var dzElement = document.getElementById('kt_dropzone');
    if (!dzElement) return;

    var uploadUrl = dzElement.dataset.dropzoneUrl;
    var csrfToken = dzElement.dataset.csrfToken;

    new Dropzone(dzElement, {
        url: uploadUrl,
        paramName: 'image',
        maxFiles: 10,
        maxFilesize: 10, // MB
        addRemoveLinks: true,
        acceptedFiles: 'image/*',
        headers: { 'X-CSRFToken': csrfToken },

        success: function (file, response) {
            if (response.id) {
                file.uploadedId = response.id;
                var input    = document.createElement('input');
                input.type   = 'hidden';
                input.name   = 'uploaded_images';
                input.value  = response.id;
                input.id     = 'uploaded-image-' + response.id;
                document.getElementById('uploaded-images-container').appendChild(input);
            }
        },

        error: function (file, response) {
            console.error('Upload error', response);
            var msg = (typeof response === 'object' && response.error) ? JSON.stringify(response.error) : response;
            file.previewElement.querySelector('.dz-error-message').innerText = msg;
        },

        removedfile: function (file) {
            if (file.uploadedId) {
                var input = document.getElementById('uploaded-image-' + file.uploadedId);
                if (input) input.remove();

                var deleteUrl = dzElement.dataset.deleteUrl.replace('/0/', '/' + file.uploadedId + '/');
                fetch(deleteUrl, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken }
                });
            }
            var el = file.previewElement;
            if (el && el.parentNode) el.parentNode.removeChild(el);
        },
    });
});
