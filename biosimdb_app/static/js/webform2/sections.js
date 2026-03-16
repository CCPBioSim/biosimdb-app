import { updateButtons, updateIndices, initializePopovers } from './helpers.js';

export function addSection(button) {
    const sectionKey = button.dataset.section;
    const container = document.querySelector(`.section-container[data-section="${sectionKey}"]`);

    const max = parseInt(container.dataset.max);
    const currentCount = container.querySelectorAll(".section-instance").length;
    if (!isNaN(max) && currentCount >= max) {
        alert(`Maximum ${max} entries allowed.`);
        return;
    }

    const firstInstance = container.querySelector(".section-instance");
    const clone = firstInstance.cloneNode(true);

    // Clear fields
    clone.querySelectorAll("input, textarea").forEach(input => input.value = "");
    clone.querySelectorAll("select").forEach(select => select.selectedIndex = 0);

    // Append clone first
    container.appendChild(clone);

    // Update indices & buttons
    updateIndices(container);
    updateButtons(container);

    // Initialize popovers for this clone
    initializePopovers(clone);
}

export function removeSection(button) {
    const instance = button.closest(".section-instance");
    const container = instance.closest(".section-container");
    instance.remove();
    updateIndices(container);
    updateButtons(container);
}