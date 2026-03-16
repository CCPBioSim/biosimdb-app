import { addSection, removeSection } from './sections.js';
import { extractMetadata, clearMetadataButton } from './metadata.js';
import { updateButtons, initializePopovers } from './helpers.js';

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".section-container").forEach(container => {
        updateButtons(container);
        initializePopovers(container); // initialize popovers for existing entries
    });
});

document.addEventListener("click", e => {
    const target = e.target;
    if (target.classList.contains("add-section")) addSection(target);
    else if (target.classList.contains("remove-section")) removeSection(target);
    else if (target.classList.contains("extract-metadata-btn")) extractMetadata(target);
    else if (target.classList.contains("clear-metadata-btn")) clearMetadataButton(target);
});


document.addEventListener("change", function(e) {

  if (!e.target.classList.contains("conditional-toggle")) return;

  const targetId = e.target.dataset.target;
  const target = document.getElementById(targetId);

  if (!target) return;

  if (e.target.checked) {
      target.style.display = "block";
      target.querySelectorAll("input,select,textarea").forEach(el => el.disabled = false);
  } else {
      target.style.display = "none";
      target.querySelectorAll("input,select,textarea").forEach(el => el.disabled = true);
  }

});
