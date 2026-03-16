export function populateMetadata(metadata, simBlock) {
    for (const name in metadata) {
        const input = simBlock.querySelector(`[name="${name}"]`);
        if (!input) continue;
        const value = metadata[name];
        if (input.tagName === "SELECT") input.value = value;
        else if (input.type === "checkbox") input.checked = value === true || value === "true" || value === 1 || value === "1";
        else input.value = value;
    }
}

export function clearMetadata(simBlock) {
    simBlock.querySelectorAll("input, select, textarea").forEach(input => {
        if (input.type === "text" || input.tagName === "TEXTAREA") input.value = "";
        else if (input.type === "file") input.value = null;
        else if (input.type === "checkbox") input.checked = false;
        else if (input.tagName === "SELECT") input.selectedIndex = 0;
    });
}

export function updateButtons(container) {
    const instances = container.querySelectorAll(".section-instance");
    instances.forEach((instance, index) => {
        const addBtn = instance.querySelector(".add-section");
        const removeBtn = instance.querySelector(".remove-section");

        if (addBtn) addBtn.style.display = (index === instances.length - 1) ? "block" : "none";
        if (removeBtn) removeBtn.style.display = (instances.length > 1) ? "block" : "none";
    });
}

export function updateIndices(container) {
    const instances = container.querySelectorAll(".section-instance");
    instances.forEach((instance, i) => {
        const newIndex = i + 1;
        instance.dataset.index = newIndex;

        // Update input names
        instance.querySelectorAll("input, textarea, select").forEach(input => {
            if (!input.name) return;
            input.name = input.name.replace(/\[\d+\]/, `[${newIndex}]`);
        });

        // Update metadata accordion
        const accordion = instance.querySelector(".metadata-accordion");
        if (accordion) {
            accordion.dataset.metaIndex = newIndex;
            const headerBtn = accordion.querySelector(".metadata-toggle");
            const collapse = accordion.querySelector(".metadata-collapse");
            const newCollapseID = `collapseMetadata${newIndex}`;
            collapse.id = newCollapseID;
            headerBtn.setAttribute("data-bs-target", `#${newCollapseID}`);
            headerBtn.setAttribute("aria-controls", newCollapseID);
            headerBtn.textContent = `Metadata ${newIndex}`;
        }

        // Update Entry number
        const entryText = instance.querySelector(".entry-number");
        if (entryText) entryText.textContent = `Entry ${newIndex}`;
    });
}

// Initialize Bootstrap popovers for any container
export function initializePopovers(container) {
    container.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
        // Dispose any existing popover to avoid duplicates
        if (el._popoverInstance) el._popoverInstance.dispose();
        el._popoverInstance = new bootstrap.Popover(el, { trigger: 'focus', html: true });
    });
}