import { populateMetadata, clearMetadata } from './helpers.js';

export async function extractMetadata(button) {
    const simBlock = button.closest(".section-instance");
    const index = simBlock.dataset.index;

    const formData = new FormData();
    simBlock.querySelectorAll("input[type=file]").forEach(input => {
        for (const file of input.files) formData.append(input.name, file);
    });
    formData.append("index", index);

    try {
        const response = await fetch("/extract_metadata", { method: "POST", body: formData });
        const metadata = await response.json();
        if (metadata.error) { alert(metadata.error); return; }
        populateMetadata(metadata, simBlock);

        // Open the accordion after extraction
        const collapseEl = simBlock.querySelector(".metadata-collapse");
        if (collapseEl && !collapseEl.classList.contains("show")) {
            new bootstrap.Collapse(collapseEl, { toggle: true });
        }
    } catch (err) {
        alert(err);
    }
}

export function clearMetadataButton(button) {
    const simBlock = button.closest(".section-instance");
    clearMetadata(simBlock);

    // Close the accordion
    const collapseEl = simBlock.querySelector(".metadata-collapse");
    if (collapseEl && collapseEl.classList.contains("show")) {
        new bootstrap.Collapse(collapseEl, { toggle: true });
    }
}