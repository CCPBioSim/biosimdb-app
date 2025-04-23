document.getElementById('addDownloadField').addEventListener('click', function() {
    const downloadFields = document.getElementById('downloadFields');
    const entries = downloadFields.querySelectorAll('.entry-block');
    const downloadCount = entries.length + 1;

    if(downloadCount < 6){
        const newFormGroupHTML = `
        <div class="entry-block">
            <br />
            <h5>Entry ${downloadCount}.</h5>

            <div class="row">

            <div class="col-sm">
                <button type="button" class="btn btn-sm btn-outline-danger remove-btn" data-type="entry">Remove</button>
            </div>

            </div>

            <div class="row form-group">

                <div class="col-sm">
                    <label for="download${downloadCount}" class="form-label">Upload topology file</label>
                    <input class="form-control" type="file" id="download${downloadCount}" name="topology_file${downloadCount}[]">
                </div>

                <div class="col-sm">
                    <label for="download${downloadCount}" class="form-label">Upload trajectory file/s</label>
                    <input class="form-control" type="file" id="download${downloadCount}" name="trajectory_file${downloadCount}[]" multiple="">
                </div>

                <div class="col-sm">
                    <label for="download${downloadCount}" class="form-label">Upload aiida archive file</label>
                    <input class="form-control" type="file" id="download${downloadCount}" name="aiida_archive_file${downloadCount}[]">
                </div>

            </div> 
        </div>
        `;

    const newField = document.createElement('div');
    newField.className = 'row form-group';
    newField.innerHTML = newFormGroupHTML;

    downloadFields.appendChild(newField);
    renumberEntries();
    }else{
    alert('Limit of 5 entries per submission')
    }
});

// renumber entries if removed
function renumberEntries() {
    const entries = document.querySelectorAll('#downloadFields .entry-block');
    entries.forEach((entry, index) => {
        const heading = entry.querySelector('h5');
        if (heading) {
            heading.textContent = `Entry ${index + 1}.`;
        }
    });
}

// remove blocks if not needed
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
