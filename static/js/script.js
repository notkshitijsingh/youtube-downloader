document.getElementById("download-type").addEventListener("change", function() {
    const type = this.value;
    const playlistResolution = document.getElementById("playlist-resolution");
    
    if (type === "playlist") {
        playlistResolution.style.display = "block";
    } else {
        playlistResolution.style.display = "none";
    }
});

document.getElementById("download-form").addEventListener("submit", function(e) {
    e.preventDefault();
    
    const downloadType = document.getElementById("download-type").value;
    const link = document.getElementById("link-input").value;
    const resolution = document.getElementById("resolution").value;

    if (!link) {
        document.getElementById("status-message").innerHTML = "Please provide a valid YouTube link.";
        return;
    }

    document.getElementById("status-message").innerHTML = "Processing download...";

    // Send data to the backend
    fetch('/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            downloadType,
            link,
            resolution
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("status-message").innerHTML = `Error: ${data.error}`;
        } else {
            // Create a download link and trigger the file download
            const downloadLink = document.createElement('a');
            downloadLink.href = data.filePath;
            downloadLink.download = true;
            downloadLink.click();
            document.getElementById("status-message").innerHTML = `Success: ${data.message}`;
        }
    })
    .catch(error => {
        document.getElementById("status-message").innerHTML = `Error: ${error.message}`;
    });
});

document.getElementById("credit-button").addEventListener('click', function(){
    window.open("https://github.com/notkshitijsingh", "_blank");
});
