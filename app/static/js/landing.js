function toggleMode() {
  const body = document.body;
  const toggleButton = document.getElementById('modeToggle');

  if (body.classList.contains('dark-mode')) {
    body.classList.remove('dark-mode');
    toggleButton.innerText = 'Dark Mode';
  } else {
    body.classList.add('dark-mode');
    toggleButton.innerText = 'Light Mode';
  }
}
