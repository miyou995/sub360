
function createToast(message) {
    // Clone the template element
    const element = htmx.find("[data-toast-template]").cloneNode(true);
    delete element.dataset.toastTemplate;

    // Set the body content
    htmx.find(element, "[data-toast-body]").innerHTML = message.message;

    // Set the header content
    const header = htmx.find(element, "[data-toast-header]");
    header.classList.add("mystyle");
    htmx.find(element, "[data-toast-tags]").innerHTML = message.tags;

    // Dynamically set color based on tags
    const tagColorClass = `bg-${message.tags}`; // e.g., bg-success, bg-danger
    element.classList.add(tagColorClass); // Add background color class
    const iconElement = htmx.find(header, ".ki-solid");
    if (iconElement) {
        iconElement.className += ` text-${message.tags}`; // Adjust icon color
    }

    // Append and show the toast
    htmx.find("[data-toast-container]").appendChild(element);
    const toast = new bootstrap.Toast(element);
    setTimeout(() => {
        toast.show();
    }, 100);
}






htmx.on("messages", (event) => {
    console.log("AAYAYYAAYA MESSAGE", event.detail.value);
    event.detail.value.forEach(createToast)
});


htmx.on("redirect_to", (event) => {
    console.log("REDIRECT OT", event.detail.value);
    setTimeout(() => {
        window.location.href = event.detail.value;
    }, 1100);
});