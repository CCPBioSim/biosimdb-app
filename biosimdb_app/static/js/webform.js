document.getElementById('addSimulationField').addEventListener('click', function () {
    const simulationFields = document.getElementById('simulationFields');
    const simulationCount = simulationFields.querySelectorAll('.entry-block').length + 1;

    if (simulationCount > 5) {
        alert('Limit of 5 entries per submission');
        return;
    }

    const newEntry = createSimulationEntry(simulationCount);
    simulationFields.appendChild(newEntry);
    renumberEntries();
});

function createSimulationEntry(index) {
    const wrapper = document.createElement('div');
    wrapper.className = 'row form-group';
    wrapper.innerHTML = getSimulationEntryHTML(index);
    return wrapper;
}

function getSimulationEntryHTML(index) {
    return `
    <div class="entry-block" data-index="${index}">
        <br />
        <h5>Entry ${index}.</h5>

        <div class="row">
            <div class="col-sm">
                <button type="button" class="btn btn-sm btn-outline-danger remove-btn" data-type="entry">Remove</button>
            </div>
        </div>

        <div class="row form-group">
            <div class="col-sm">
                <label for="simulation${index}" class="form-label">Upload topology file</label>
                <input class="form-control" type="file" id="simulation${index}" name="topology_file${index}[]">
            </div>

            <div class="col-sm">
                <label for="simulation${index}" class="form-label">Upload trajectory file/s</label>
                <input class="form-control" type="file" id="simulation${index}" name="trajectory_file${index}[]" multiple>
            </div>

            <div class="col-sm">
                <label for="simulation${index}" class="form-label">Upload aiida archive file</label>
                <input class="form-control" type="file" id="simulation${index}" name="aiida_archive_file${index}[]">
            </div>

            <div class="mt-3 d-grid gap-2">
                <button type="button" class="btn btn-secondary btn-sm extract-metadata-btn" id="extractMetadataField${index}">Add entry metadata</button>
            </div>

            ${getAccordionHTML(index)}
        </div> 
    </div>
    `;
}

// Add the metadata accordion to the simulation entry
function getAccordionHTML(index) {
    return `
        <div class="accordion mt-3" id="metadataAccordionEntry${index}">
            <div class="accordion-item">
                <h2 class="accordion-header" id="headingMetadata${index}">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseMetadata${index}" aria-expanded="false" aria-controls="collapseMetadata${index}">
                    Entry ${index} Metadata
                </button>
                </h2>
                <div id="collapseMetadata${index}" class="accordion-collapse collapse" aria-labelledby="headingMetadata${index}" data-bs-parent="#metadataAccordionEntry${index}">

                <div class="accordion-body metadata-fields${index}">
                    <!-- Auto-populate metadata here -->
                </div>

                </div>
            </div>
        </div>
    `;
}

// renumber entries if removed
function renumberEntries() {
    const entries = document.querySelectorAll('#simulationFields .entry-block');
    entries.forEach((entry, index) => {
        const heading = entry.querySelector('h5');
        if (heading) {
            heading.textContent = `Entry ${index + 1}.`;
        }
        // update the accordion title
        const metadataButton = entry.querySelector('.accordion-button');
        if (metadataButton) {
            metadataButton.textContent = `Entry ${index + 1} Metadata`;
        }
    });
}

// remove entry blocks if not needed
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('remove-btn')) {
        const type = e.target.getAttribute('data-type');

        // Find the corresponding block to remove
        let blockClass = '';
        if (type === 'author') blockClass = 'author-block';
        else if (type === 'entry') blockClass = 'entry-block';
        else if (type === 'citation') blockClass = 'citation-block';

        const container = e.target.closest(`.${blockClass}`);
        if (container) {
            container.remove();

            // Optional: Renumber if it's an entry
            if (type === 'entry') renumberEntries();
        }
    }
});

// add author section of form when button is clicked
document.getElementById('addAuthorField').addEventListener('click', function() {
    const authorFields = document.getElementById('authorFields');
    const authorCount = authorFields.childElementCount + 1; // depends on N uploads
    if(authorCount < 16){
        const newFormGroupHTML = `
        <div class="row author-block">
            <div class="col-sm">
            <label for="author${authorCount}" class="form-label">Additional author/s</label>
            <input type="text" class="form-control" id="author${authorCount}" placeholder="Enter full name of additional author" name="author_name[]">
            </div>

            <div class="col-sm">
                <button type="button" class="btn btn-sm btn-outline-danger remove-btn" data-type="author">Remove</button>
            </div>

        </div>
    `;

    const newField = document.createElement('div');
    newField.className = 'row form-group';
    newField.innerHTML = newFormGroupHTML;

    authorFields.appendChild(newField);
    }else{
    alert('Limit of 15 authors per submission')
    }
});

// add citation section of form when button is clicked
document.getElementById('addCitationField').addEventListener('click', function() {
    const citationFields = document.getElementById('citationFields');
    const citationCount = citationFields.childElementCount + 1; // depends on N uploads
    if(citationCount < 11){
        const newFormGroupHTML = `
        <div class="row citation-block">
            <div class="col-sm">
            <label for="citation${citationCount}" class="form-label">Additional citation</label>
            <input type="text" class="form-control" id="author${citationCount}" placeholder="Include DOI of the published work related to uploaded simulation/s" name="citation_name[]">
            </div>

            <div class="col-sm">
                <button type="button" class="btn btn-sm btn-outline-danger remove-btn" data-type="citation">Remove</button>
            </div>

        </div>
    `;

    const newField = document.createElement('div');
    newField.className = 'row form-group';
    newField.innerHTML = newFormGroupHTML;

    citationFields.appendChild(newField);
    }else{
    alert('Limit of 10 citations per submission')
    }
});


// add metadata to form by parsing topology and traj
document.addEventListener('click', function (e) {
    if (e.target && e.target.classList.contains('extract-metadata-btn')) {
        const entry = e.target.closest('.entry-block');
        const index = entry.getAttribute('data-index');

        const formData = new FormData();
        const topoInput = entry.querySelector(`[name="topology_file${index}[]"]`);
        const trajInput = entry.querySelector(`[name="trajectory_file${index}[]"]`);

        if (!topoInput || !trajInput) return alert('Please select both topology and trajectory files.');

        if (topoInput.files.length > 0) formData.append('topology', topoInput.files[0]);
        if (trajInput.files.length > 0) formData.append('trajectory', trajInput.files[0]);
        formData.append('entry_index', index);

        fetch('/parse-metadata', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {

            renderMetadataFields(index, entry, data);

            // Automatically show metadata accordion on successful parse
            const accordion = entry.querySelector(`#collapseMetadata${index}`);
            const bsCollapse = new bootstrap.Collapse(accordion, { toggle: false });
            bsCollapse.show();
        
        })
        .catch(err => {
            console.error('Metadata parse error:', err);
            alert('Failed to extract metadata.');
        });
    }
});

// Populate the metadata into the webform html
function renderMetadataFields(index, entry, metadata) {
    const container = entry.querySelector(`.metadata-fields${index}`);
    container.innerHTML = ''; // Clear previous metadata fields

    // Check for error and display it clearly
    if (metadata.error) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger';
        alert.role = 'alert';
        alert.textContent = `Metadata extraction failed: ${metadata.error}`;
        container.appendChild(alert);
        return;
    }

    for (const [key, value] of Object.entries(metadata)) {
        const label = document.createElement('label');
        label.className = 'form-label mt-2';
        label.textContent = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        label.setAttribute('for', `${key}`);

        const input = document.createElement(
            typeof value === 'string' && value.length > 100 ? 'textarea' : 'input'
        );
        input.className = `form-control ${key}-field`;
        input.name = `parsed_${key}${entry.dataset.index}`;
        input.value = value;
        if (input.tagName === 'TEXTAREA') {
            input.rows = 3;
        }

        container.appendChild(label);
        container.appendChild(input);
    }
}