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

            <div class="mt-3 d-grid gap-2">
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

            <div class="mt-3 d-grid gap-2">
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

// Add a new entry block if add button clicked
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

// create new simulation entry block with fields
function createSimulationEntry(index) {
    const wrapper = document.createElement('div');
    wrapper.className = 'row form-group';
    wrapper.innerHTML = getSimulationEntryHTML(index);
    return wrapper;
}

// populate a new entry block with upload file fields
function getSimulationEntryHTML(index) {
    return `
    <div class="entry-block" data-index="${index}">
        <br />
        <h5>Entry ${index}.</h5>

        <div class="row">
            <div class="mt-3 d-grid gap-2">
                <button type="button" class="btn btn-sm btn-outline-danger remove-btn" data-type="entry">Remove Entry</button>
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
                <div class="row">
                    <div class="col-sm mt-3 d-grid">
                        <!-- Button for extracting metadata from files -->
                        <button type="button" class="btn btn-outline-primary btn-sm extract-metadata-btn" id="extractMetadataField${index}">Add entry metadata</button>
                    </div>
                    <div class="col-sm mt-3 d-grid">
                        <!-- Button to clear metadata -->
                        <button type="button" class="btn btn-outline-warning btn-sm clear-metadata-btn" id="clearMetadataField${index}">Clear Metadata</button>
                    </div>
                </div>
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

            // Renumber if it's an entry
            if (type === 'entry') renumberEntries();
        }
    }
});

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

// add metadata to simulation entry by parsing topology and trajectory
document.addEventListener('click', function (e) {
    // continue if the user clicks on the "Extract Metadata" button
    if (e.target && e.target.classList.contains('extract-metadata-btn')) {
        // Find closest ancestor element of the clicked button that has the class entry-block, which each simulation entry is wrapped in
        const entry = e.target.closest('.entry-block');
        // Get the data-index attribute of that .entry-block, helps identify which entry is being worked on
        const index = entry.getAttribute('data-index');

        // Create new FormData object, used to send files to the server easily
        const formData = new FormData();
        // Find input fields inside entry for uploading topology and trajectory files, matches based on the name attribute
        const topoInput = entry.querySelector(`[name="topology_file${index}[]"]`);
        const trajInput = entry.querySelector(`[name="trajectory_file${index}[]"]`);

        // If input fields can't be found (would be strange), alert the user and stop
        // if (!topoInput || !trajInput) return alert('Please select both topology and trajectory files.');

        // If file has been selected in the input fields: Add to formData. 
        if (topoInput.files.length > 0) formData.append('topology', topoInput.files[0]);
        if (trajInput.files.length > 0) formData.append('trajectory', trajInput.files[0]);
        // Also add entry_index so server knows which entry it belongs to.
        formData.append('entry_index', index);

        // Sends POST request to Flask server route /parse-metadata.
        // The formData (with uploaded files) is included in the body.
        fetch('/parse-metadata', {
            method: 'POST',
            body: formData
        })
        // When server responds, parse the response as JSON.
        .then(res => res.json())
        // Now data will be a JavaScript object representing your metadata.
        .then(data => {

            // populate the webform with the parsed metadata fields
            renderMetadataFields(index, entry, data);

            // Automatically show metadata accordion on successful parse
            // Locate metadata accordion section in entry.
            const accordion = entry.querySelector(`#collapseMetadata${index}`);
            const bsCollapse = new bootstrap.Collapse(accordion, { toggle: false });
            // Use Bootstrap's Collapse API to programmatically open (show) the accordion after metadata is populated.
            bsCollapse.show();
        
        })
        // If any error happens during the fetch or parsing, log error and show alert message
        .catch(err => {
            console.error('Metadata parse error:', err);
            alert('Failed to extract metadata.');
        });
    }
});

// dynamically populate the metadata into the simulation entry accordion
function renderMetadataFields(index, entry, metadata) {
    const container = entry.querySelector(`.metadata-fields${index}`);
    // container.innerHTML = ''; // Clear previous metadata fields

    // Check for error in metadata key and display it
    // This means the file formats couldn't be parsed
    if (metadata.error) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger';
        alert.role = 'alert';
        alert.textContent = `Metadata extraction failed: ${metadata.error}`;
        container.appendChild(alert);
        return; // don't render rest of metadata
    }

    // if there is an alert key, display it
    // this means files haven't been uploaded to extract metadata
    if (metadata.alert) {
        // alert(metadata.alert);
        const alert = document.createElement('div');
        alert.className = 'alert alert-warning';
        alert.role = 'alert';
        alert.textContent = `Automatic metadata extraction failed: ${metadata.alert}`;
        container.appendChild(alert);
        return; // comment to continue rendering rest of metadata
    }

    // Sort groups by their number prefix
    // const groupEntries = Object.entries(metadata);
    // groupEntries.sort((a, b) => {
    //     const aNum = parseInt(a[0].split('_')[0], 10); // get number before first _
    //     const bNum = parseInt(b[0].split('_')[0], 10);
    //     return aNum - bNum;
    // });

    // --- Capture existing field values before clearing ---
    const existingData = {};
    container.querySelectorAll('input, textarea').forEach(input => {
        let rawName = input.getAttribute('name') || "";
        rawName = rawName.replace(/^parsed_/, '');   // remove parsed_ prefix
        rawName = rawName.replace(new RegExp(index + '$'), '');  // remove trailing index
        rawName = rawName.replace(/\[\]$/, ''); // remove any [] at end

        if (input.value.trim() !== "") {
            existingData[rawName] = input.value.trim();
        }
    });

    // --- Clear the container ---
    container.innerHTML = '';

    // --- Merge server metadata and existing user edits ---
    const mergedMetadata = {};

    for (const [group, groupData] of Object.entries(metadata)) {
        mergedMetadata[group] = {};
        for (const [key, serverValue] of Object.entries(groupData)) {
            if (existingData.hasOwnProperty(key)) {
                mergedMetadata[group][key] = existingData[key]; // User wins
            } else if (serverValue !== "" && serverValue !== null) {
                mergedMetadata[group][key] = serverValue; // Else use server
            } else {
                mergedMetadata[group][key] = ""; // Otherwise blank
            }
        }
    }

    // Loop through each metadata group (e.g., System Details, Simulation Settings)
    //for (const [groupName, fields] of Object.entries(metadata)) {
    for (const [groupName, fields] of Object.entries(mergedMetadata)) {

        // ignore the alert key if returned from server
        if (groupName === 'alert') continue;

        // Convert group name from snake_case to readable format
        const readableGroupName = groupName
            .replace(/^\d+_/, '')   // remove leading "1_", "2_", etc.
            //.replace(/^[A-Z]_/, '')   // remove one capital letter and underscore at start
            .replace(/_/g, ' ') // replace underscores with spaces
            .replace(/\b\w/g, letter => letter.toUpperCase()); // capitalize first letter of each word


        const groupTitle = document.createElement('h6');
        groupTitle.textContent = readableGroupName;
        groupTitle.className = 'mt-3 mb-2 fw-bold'; // Styling the group header
        container.appendChild(groupTitle);

        // Sort the fields: filled (non-empty) first, then empty
        const sortedFields = Object.entries(fields).sort(([keyA, valueA], [keyB, valueB]) => {
            const isEmptyA = (Array.isArray(valueA) ? valueA.join('').trim() === '' : !valueA);
            const isEmptyB = (Array.isArray(valueB) ? valueB.join('').trim() === '' : !valueB);
            return isEmptyA - isEmptyB; // false (0) comes before true (1)
        });

        // Now loop through each field inside the group
        // iterate over all key value pairs and render
        for (const [key, value] of sortedFields) {
            const label = document.createElement('label');
            label.className = 'form-label mt-2';
            label.textContent = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            label.setAttribute('for', `${key}`);

            const input = document.createElement(
                (typeof value === 'string' && value.length > 100) ? 'textarea' : 'input'
            );
            input.className = `form-control ${key}-field`;
            input.name = `parsed_${key}${entry.dataset.index}`;
            input.value = (Array.isArray(value)) ? value.join(', ') : value;

            if (input.tagName === 'TEXTAREA') {
                input.rows = 3;
            }

            container.appendChild(label);
            container.appendChild(input);
        }
    }
}

// Clear metadata fields for a simulation entry
document.addEventListener('click', function (e) {
    if (e.target && e.target.classList.contains('clear-metadata-btn')) {
        const entry = e.target.closest('.entry-block');
        const index = entry.getAttribute('data-index');

        const container = entry.querySelector(`.metadata-fields${index}`);

        if (container) {
            container.innerHTML = ''; // Simply remove all existing metadata fields
        }

        // Optionally, collapse the accordion again if you want
        const accordion = entry.querySelector(`#collapseMetadata${index}`);
        if (accordion) {
            const bsCollapse = new bootstrap.Collapse(accordion, { toggle: false });
            bsCollapse.hide();
        }
    }
});