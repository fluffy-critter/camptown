window.addEventListener("load", () => {

    // Only one disclosure should be open at a time
    disclosures = document.querySelectorAll('input[type="checkbox"]');
    disclosures.forEach((disclosure) => {
        disclosure.addEventListener("change", () => {
            if (disclosure.checked) {
                disclosures.forEach((other) => {
                    if (disclosure != other) {
                        other.checked = false;
                    }
                });
            }
        });
    });
});

