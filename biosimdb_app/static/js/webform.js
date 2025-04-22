document.getElementById('addDownloadField').addEventListener('click', function() {
    var downloadFields = document.getElementById('downloadFields');
    var downloadCount = downloadFields.childElementCount - 4; // depends on N uploads
    if(downloadCount < 6){
    var newFormGroupHTML = `
    <div>
        <br />
        <h5>Entry ${downloadCount}.</h5>
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

    var newField = document.createElement('div');
    newField.className = 'row form-group';
    newField.innerHTML = newFormGroupHTML;

    downloadFields.appendChild(newField);
    }else{
    alert('Limit of 5 entries per submission')
    }
});


document.getElementById('addAuthorField').addEventListener('click', function() {
    var authorFields = document.getElementById('authorFields');
    var authorCount = authorFields.childElementCount + 1; // depends on N uploads
    if(authorCount < 16){
    var newFormGroupHTML = `
    <div class="row">
        <div class="col-sm">
        <label for="author${authorCount}" class="form-label">Additional author/s</label>
        <input type="text" class="form-control" id="author${authorCount}" placeholder="Enter full name of additional author" name="author_name[]">
        </div>
    </div>
    `;

    var newField = document.createElement('div');
    newField.className = 'row form-group';
    newField.innerHTML = newFormGroupHTML;

    authorFields.appendChild(newField);
    }else{
    alert('Limit of 15 authors per submission')
    }
});


document.getElementById('addCitationField').addEventListener('click', function() {
    var citationFields = document.getElementById('citationFields');
    var citationCount = citationFields.childElementCount + 1; // depends on N uploads
    if(citationCount < 11){
    var newFormGroupHTML = `
    <div class="row">
        <div class="col-sm">
        <label for="citation${citationCount}" class="form-label">Additional citation</label>
        <input type="text" class="form-control" id="author${citationCount}" placeholder="Include DOI of the published work related to uploaded simulation/s" name="citation_name[]">
        </div>
    </div>
    `;

    var newField = document.createElement('div');
    newField.className = 'row form-group';
    newField.innerHTML = newFormGroupHTML;

    citationFields.appendChild(newField);
    }else{
    alert('Limit of 10 citations per submission')
    }
});
