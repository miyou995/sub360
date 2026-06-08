const STACKED_MODAL_IDS = [
    'kt_modal',
    'kt_modal_stacked_2',
    'kt_modal_stacked_3',
];

function getOpenStackedModalIds() {
    return STACKED_MODAL_IDS.filter((modalId) => {
        const modal = document.getElementById(modalId);
        return modal && modal.classList.contains('show');
    });
}

function getTopStackedModalId() {
    const openModals = getOpenStackedModalIds();
    return openModals.length ? openModals[openModals.length - 1] : null;
}

// function getNextStackedModalId() {
//     const openModals = getOpenStackedModalIds();
//     if (!openModals.length) {
//         return 'kt_modal';
//     }
//     const currentTop = openModals[openModals.length - 1];
//     const currentIndex = STACKED_MODAL_IDS.indexOf(currentTop);
//     if (currentIndex === -1) {
//         return 'kt_modal';
//     }
//     return STACKED_MODAL_IDS[Math.min(currentIndex + 1, STACKED_MODAL_IDS.length - 1)];
// }

function getModalContentId(modalId) {
    return modalId === 'kt_modal' ? 'kt_modal_content' : `${modalId}_content`;
}

// function addOrReplaceQueryParam(url, key, value) {
//     const [baseUrl, hash = ''] = url.split('#');
//     const [path, queryString = ''] = baseUrl.split('?');
//     const params = new URLSearchParams(queryString);
//     params.set(key, value);
//     const query = params.toString();
//     const withParam = query ? `${path}?${query}` : path;
//     return hash ? `${withParam}#${hash}` : withParam;
// }

// ── closeModal HTMX event ────────────────────────────────────────────────────
htmx.on('closeModal', (event) => {
    const targetModalId = event.detail && event.detail.value ? event.detail.value : getTopStackedModalId();
    if (!targetModalId) {
        return;
    }
    const modalEl = document.getElementById(targetModalId);
    if (!modalEl) {
        return;
    }
    const modal = bootstrap.Modal.getInstance(modalEl) || bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.hide();
});

// htmx.logAll();



// document.addEventListener("htmx:load", function() {
//     KTComponents.init();
// });


htmx.onLoad(function(){
	KTComponents.init();
})



htmx.on('total_revenu', (e) => {
    document.getElementById('theTotalId').innerHTML = e.detail.value;

});


document.addEventListener('htmx:afterSettle', (e) => {
    // console.log("htmx:afterSettle");
    const eventsBlock = document.querySelector("#eventsId");

    if (eventsBlock) {
        setTimeout(function () {
            preInitHTMXCalendar();
        }, 100)
    }
});




document.addEventListener('DOMContentLoaded', function () {
    // console.log("Document loaaaded lets call the callendar");

    const eventsBlock = document.querySelector("#eventsId");
    if (eventsBlock) {
        preInitHTMXCalendar();
    }
});


document.addEventListener("htmx:load", function () {
    KTComponents.init();
});


window.addEventListener('load', () => {
    const toastrMessages = localStorage.getItem('toastrMessages');
    if (toastrMessages) {
        const messages = JSON.parse(toastrMessages);
        messages.forEach(msg => {
            if (msg.tags.includes('toastr')) {
                // Display Toastr notifications based on the message type
                if (msg.tags.includes('error')) {
                    toastr.error(msg.message);
                } else if (msg.tags.includes('warning')) {
                    toastr.warning(msg.message);
                } else if (msg.tags.includes('info')) {
                    toastr.info(msg.message);
                } else if (msg.tags.includes('success')) {
                    toastr.success(msg.message);
                }
            }
        });
        // Clear the stored messages to avoid showing them again
        localStorage.removeItem('toastrMessages');
    }
});









// function isModalOpen(modalId) {
//     const modalElm = document.getElementById(modalId);
//     if (!modalElm) return false;
//     return modalElm.classList.contains('show');
// }

/** Returns the topmost visible modal's content container element, or null. */
// function getActiveModalContent() {
//     const topModalId = getTopStackedModalId();
//     if (topModalId) {
//         return document.getElementById(getModalContentId(topModalId));
//     }
//     // Fallback: any visible .modal
//     const visible = Array.from(document.querySelectorAll('.modal.show'));
//     return visible.length ? visible[visible.length - 1].querySelector('.modal-content') : null;
// }


function optionFormat(item) {
    if (!item.id) {
        return item.text;
    }

    // pull the attributes once
    const iconUrl = item.element.getAttribute('data-kt-rich-content-icon');
    const subText = item.element.getAttribute('data-kt-rich-content-subcontent');

    // build your template string conditionally
    let template = '<div class="d-flex align-items-center">';

    if (iconUrl) {
        template +=
            '<img src="' + iconUrl +
            '" class="rounded-circle h-40px me-3" alt="' + item.text + '"/>';
    }

    template += '<div class="d-flex flex-column">';
    template += '<span class="fs-4 fw-bold lh-1">' + item.text + '</span>';

    if (subText) {
        template +=
            '<span class="text-muted fs-5">' + subText + '</span>';
    }

    template += '</div></div>';

    const span = document.createElement('span');
    span.innerHTML = template;
    return $(span);
}


function initializeSelect2(containerEl) {
    // containerEl: limit initialization to elements inside this node.
    // When undefined, initialize all uninitialized selects on the page.
    const scope = containerEl || document;

    // Determine the correct dropdownParent for each element based on which
    // modal it lives in (supports arbitrary stack depth).
    $(scope).find('[data-control="select2"]').addBack('[data-control="select2"]').each(function () {
        const element = this;
        // Skip if already initialized in the current context
        if ($(element).data('select2')) {
            $(element).select2('destroy');
        }

        // Find the nearest open modal ancestor for this element
        const modalAncestor = element.closest('.modal.show');
        let dropdownParent = null;
        if (modalAncestor) {
            dropdownParent = $(modalAncestor.querySelector('.modal-content'));
        }

        const options = { dropdownParent: dropdownParent };
        if (element.getAttribute('data-hide-search') === 'true') {
            options.minimumResultsForSearch = Infinity;
        }
        if (element.getAttribute('data-kt-rich-content') === 'true') {
            options.templateResult = optionFormat;
            options.templateSelection = optionFormat;
        }
        $(element).select2(options);
    });
}


htmx.on('htmx:afterSwap', (e) => {
    KTMenu.createInstances();
    // Initialize only selects inside the swapped target to avoid double-init
    const target = e.detail && e.detail.target ? e.detail.target : document;
    setTimeout(() => {
        initializeSelect2(target);
    }, 100);
});

// Run after Bootstrap modal hidden — stack-aware cleanup
window.addEventListener('hidden.bs.modal', (e) => {
    const closedModalId = e.target ? e.target.id : null;
    if (!closedModalId) {
        return;
    }

    const modalContent = document.getElementById(getModalContentId(closedModalId));
    if (modalContent) {
        modalContent.innerHTML = '';
    }

    // Keep body locked while at least one stacked modal remains open.
    if (document.querySelector('.modal.show')) {
        document.body.classList.add('modal-open');
    }

    // Reinitialize Select2 in any remaining open modals
    document.querySelectorAll('.modal.show').forEach((modalEl) => {
        initializeSelect2(modalEl);
    });
});


window.addEventListener("DOMContentLoaded", (e) => {
    // Use event delegation on document so these handlers are registered once
    // and fire for dynamically added elements too (avoids duplicate registration
    // that occurred with the previous htmx:load-based approach, where a new
    // listener was added for every element HTMX processed after each swap).
    $(document).on('select2:select select2:unselect', '.per-page-select', function (e) {
        const form = document.getElementById('filterForm');
        if (form) {
            form.dispatchEvent(new Event('change'));
        }
    });
    $(document).on('select2:select select2:unselect', '.form-select', function (e) {
        $(this).closest('select').get(0).dispatchEvent(new Event('changed'));
        const form = $(this).closest('form');
        if (form.length > 0) {
            form.get(0).dispatchEvent(new Event('change'));
        }
    });
});



function getSubmitButtonForElement(element) {
    if (!element) return null;
    const form = element.tagName === 'FORM' ? element : element.closest('form');
    if (!form) return null;
    return form.querySelector('.js-submit-button, #submitButton, button[type="submit"]');
}

htmx.on('htmx:beforeSend', (e) => {
    const button = getSubmitButtonForElement(e.detail && e.detail.elt);
    if (button) {
        button.setAttribute('data-kt-indicator', 'on');
    }
});

htmx.on('htmx:afterRequest', (e) => {
    const button = getSubmitButtonForElement(e.detail && e.detail.elt);
    if (button && button.hasAttribute('data-kt-indicator')) {
        button.removeAttribute('data-kt-indicator');
    }
});




htmx.on("modal_resize", (event) => {
    // Target the dialog of the currently active (topmost) modal
    const topModalId = getTopStackedModalId();
    const dialogId = topModalId ? `${topModalId}_dialog` : 'kt_modal_dialog';
    const modal = document.getElementById(dialogId);
    if (!modal) return;

    // Reset to default modal classes first
    modal.className = "modal-dialog modal-dialog-centered";

    // Apply new size classes passed from Django
    if (event.detail && event.detail.value) {
        modal.classList.add(...event.detail.value.split(" "));
    }
});




// function resolveSelect2DropdownParent(element) {
//     const explicitParent = element.getAttribute('data-dropdown-parent');
//     if (explicitParent) {
//         const parentElement = document.querySelector(explicitParent);
//         if (parentElement) {
//             return $(parentElement);
//         }
//     }

//     const modalAncestor = element.closest('.modal.show');
//     if (modalAncestor) {
//         const modalContent = modalAncestor.querySelector('.modal-content');
//         return modalContent ? $(modalContent) : null;
//     }

//     return null;
// }

