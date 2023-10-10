function syncText() {
    document.getElementById('text').value = document.getElementById('editor').innerHTML;
    setTimeout(syncText, 500);
  }
  syncText();