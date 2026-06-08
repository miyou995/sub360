createSelect2 = function () {
    // Check if jQuery included
    if (typeof jQuery == 'undefined') {
        return;
    }

    // Check if select2 included
    if (typeof $.fn.select2 === 'undefined') {
        return;
    }

    var elements = [].slice.call(document.querySelectorAll('[data-control="select2"], [data-kt-select2="true"]'));

    elements.map(function (element) {
        if (element.getAttribute("data-kt-initialized") === "1") {
            return;
        }

        var options = {
            dir: document.body.getAttribute('direction')
        };

        if (element.getAttribute('data-hide-search') == 'true') {
            options.minimumResultsForSearch = Infinity;
        }

        $(element).select2(options);

        // Handle Select2's KTMenu parent case
        if (element.hasAttribute('data-dropdown-parent') && element.hasAttribute('multiple')) {
            var parentEl = document.querySelector(element.getAttribute('data-dropdown-parent'));

            if (parentEl && parentEl.hasAttribute("data-kt-menu")) {
                var menu = KTMenu.getInstance(parentEl);
                
                if (!menu) {
                    menu = new KTMenu(parentEl);
                }

                if (menu) {
                    $(element).on('select2:unselect', function (e) {
                        element.setAttribute("data-multiple-unselect", "1");
                    });

                    menu.on("kt.menu.dropdown.hide", function(item) {
                        if (element.getAttribute("data-multiple-unselect") === "1") {
                            element.removeAttribute("data-multiple-unselect");
                            return false;
                        }
                    });
                }                    
            }                
        }

        element.setAttribute("data-kt-initialized", "1");
    });
}

createSelect2();