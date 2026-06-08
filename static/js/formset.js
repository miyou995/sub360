/**
 * Formset management – automatic, data-attribute driven.
 * Vanilla JS, no jQuery dependency required.
 *
 * ── HTML contract ──────────────────────────────────────────────────────────
 *
 *  Container (the div wrapping all rows):
 *    <div id="options-container"
 *         data-formset
 *         data-prefix="options"
 *         data-row-class="option-row"
 *         data-template="empty-option-form">
 *
 *  Add button (anywhere on the page, references container by id):
 *    <button data-formset-add="options-container">Add</button>
 *
 *  Remove button (must live inside a row, inside the container):
 *    <button data-formset-remove>Remove</button>
 *
 *  Django's TOTAL_FORMS input is resolved automatically from the prefix:
 *    id_<prefix>-TOTAL_FORMS
 *
 *  ── Nested formset support ────────────────────────────────────────────
 *
 *  For nested formsets (formsets inside formset rows), add:
 *    data-placeholder="__nested__"   on the nested container
 *
 *  The outer template uses __prefix__ for its own index, and nested
 *  templates use __nested__ so both levels can be resolved independently.
 *
 * ───────────────────────────────────────────────────────────────────────────
 */

(function () {
    'use strict';

    // Note: isModalOpen, optionFormat, and initializeSelect2 are defined in octopus.js
    // to avoid duplication and ensure global availability


    /** Derive Django's TOTAL_FORMS input id from the formset prefix. */
    function totalFormsInputId(prefix) {
        return 'id_' + prefix + '-TOTAL_FORMS';
    }


    /**
     * Single source of truth for the form count.
     * Counts every row (visible or hidden) inside the container and writes
     * the value to the TOTAL_FORMS management input.
     *
     * @param {HTMLElement} container – the element with [data-formset]
     */
    function updateFormCount(container) {
        const prefix   = container.dataset.prefix;
        const rowClass = container.dataset.rowClass;
        const input    = document.getElementById(totalFormsInputId(prefix));

        if (!input) {
            console.warn('[formset.js] updateFormCount: TOTAL_FORMS input not found for prefix:', prefix);
            return;
        }

        const rows = Array.from(container.children).filter(function (child) {
            return child.classList && child.classList.contains(rowClass);
        });

        const formRegex = new RegExp('(' + prefix + '-)(\\d+)(-)', 'g');

        function replaceIndexedValue(value, index) {
            if (!value) return value;
            formRegex.lastIndex = 0;
            if (!formRegex.test(value)) return value;
            formRegex.lastIndex = 0;
            return value.replace(formRegex, '$1' + index + '$3');
        }

        function reindexElementAttributes(element, index) {
            if (element.name) {
                element.name = replaceIndexedValue(element.name, index);
            }
            if (element.id) {
                element.id = replaceIndexedValue(element.id, index);
            }
            if (element.htmlFor) {
                element.htmlFor = replaceIndexedValue(element.htmlFor, index);
            }

            if (!element.attributes) return;

            Array.from(element.attributes).forEach(function (attribute) {
                if (
                    attribute.name.startsWith('data-')
                    || attribute.name === 'aria-describedby'
                    || attribute.name === 'aria-labelledby'
                ) {
                    const nextValue = replaceIndexedValue(attribute.value, index);
                    if (nextValue !== attribute.value) {
                        element.setAttribute(attribute.name, nextValue);
                    }
                }
            });
        }

        function reindexTree(root, index) {
            if (root.nodeType === Node.ELEMENT_NODE) {
                reindexElementAttributes(root, index);
            }
            root.querySelectorAll('*').forEach(function (element) {
                reindexElementAttributes(element, index);
            });
        }

        rows.forEach(function (row, index) {
            reindexTree(row, index);

            // ── Reindex content inside <template> elements (nested templates) ──
            row.querySelectorAll('template').forEach(function (tmpl) {
                reindexTree(tmpl.content, index);
            });

            const rowIndexBadge = row.querySelector('[data-formset-index]');
            if (rowIndexBadge) {
                rowIndexBadge.textContent = String(index + 1);
            }
        });

        // Include hidden rows – Django still needs to know they exist when DELETE is ticked.
        input.value = rows.length;
    }

    /**
     * Clone the empty-form template, stamp the next index over __prefix__,
     * append the new row to the container, then delegate the count update
     * to updateFormCount.
     *
     * @param {HTMLElement} container – the element with [data-formset]
     */
    function addFormRow(container) {
        const prefix     = container.dataset.prefix;
        const templateId = container.dataset.template;
        const placeholder = container.dataset.placeholder || '__prefix__';
        const template   = document.getElementById(templateId);
        const input      = document.getElementById(totalFormsInputId(prefix));

        if (!template || !input) {
            console.warn('[formset.js] addFormRow: Missing template or TOTAL_FORMS for container:', container.id);
            return;
        }

        const nextIndex = parseInt(input.value, 10);
        const placeholderRegex = new RegExp(placeholder, 'g');
        const html = template.innerHTML.replace(placeholderRegex, nextIndex).trim();

        const fragment = document.createRange().createContextualFragment(html);
        if (!fragment.firstElementChild) {
            console.warn('[formset.js] addFormRow: Empty template for container:', container.id);
            return;
        }

        container.appendChild(fragment);

        // Initialize nested formset counts in the newly added row
        var newRow = container.lastElementChild;
        if (newRow) {
            newRow.querySelectorAll('[data-formset]').forEach(function (nestedContainer) {
                updateFormCount(nestedContainer);
            });
        }

        // Delegate – updateFormCount is the only place that writes the count.
        updateFormCount(container);
        if (typeof window.initializeSelect2 === 'function') {
            window.initializeSelect2(newRow);
        }
        if (typeof window.initQuillEditors === 'function') {
            console.log('Initializing Quill editors in new formset row');
            window.initQuillEditors(newRow);
        }
    }

    /**
     * Hide or remove a formset row and mark its DELETE checkbox when present.
     * Delegates the count update to updateFormCount.
     *
     * @param {HTMLElement} btn – the remove button inside the row
     */
    function removeFormRow(btn) {
        const container = btn.closest('[data-formset]');
        if (!container) return;

        const row = btn.closest('.' + container.dataset.rowClass);
        if (!row) return;

        // Django formsets render a DELETE field for every form (including extra/new forms),
        // so we cannot use its presence to know whether the row exists in DB.
        // For ModelFormSets/InlineFormSets, the hidden `-id` field will have a value only
        // for persisted instances.
        const objectIdInput = row.querySelector('input[type="hidden"][name$="-id"]');
        const hasPersistedInstance = Boolean(objectIdInput && String(objectIdInput.value || '').trim());

        if (hasPersistedInstance) {
            const deleteInput = row.querySelector('input[name$="-DELETE"]');
            if (!deleteInput) {
                console.warn('[formset.js] removeFormRow: Missing DELETE input for persisted row.');
                return;
            }
            // Existing DB row: only mark for deletion.
            deleteInput.checked = true;
        } else {
            // New (unsaved) row: remove from the DOM entirely.
            row.remove();
        }

        // Delegate – updateFormCount is the only place that writes the count.
        updateFormCount(container);
    }

    // ── Single event listener handles every formset on the page ────────────

    document.addEventListener('click', function (e) {
        const addBtn = e.target.closest('[data-formset-add]');
        if (addBtn) {
            const container = document.getElementById(addBtn.dataset.formsetAdd);
            if (container) addFormRow(container);
            return;
        }

        const removeBtn = e.target.closest('[data-formset-remove]');
        if (removeBtn) {
            removeFormRow(removeBtn);
        }
    });

    function syncAllFormsets() {
        document.querySelectorAll('[data-formset]').forEach(function (container) {
            updateFormCount(container);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', syncAllFormsets);
    } else {
        syncAllFormsets();
    }

    // ── Public API (for programmatic use or legacy inline handlers) ─────────

    window.formset = {
        /** Manually trigger an add on a container element or its id. */
        add: function (containerOrId) {
            const el = typeof containerOrId === 'string'
                ? document.getElementById(containerOrId)
                : containerOrId;
            if (el) addFormRow(el);
        },
        /** Manually trigger a remove given the remove button element. */
        remove: function (btn) {
            removeFormRow(btn);
        },
        /** Manually sync the count for a container element or its id. */
        updateCount: function (containerOrId) {
            const el = typeof containerOrId === 'string'
                ? document.getElementById(containerOrId)
                : containerOrId;
            if (el) updateFormCount(el);
        },
        syncAll: syncAllFormsets,
    };

})();