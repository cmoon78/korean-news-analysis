document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let formData = new FormData(this);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/news_explore';
        } else {
            console.error(data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
