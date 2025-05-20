// dark-mode-toggle.js

document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('dark-mode-toggle');
    let darkMode = false;

    toggleBtn.addEventListener('click', function() {
        darkMode = !darkMode;

        if (darkMode) {
            // Enable dark mode
            document.body.style.backgroundColor = '#333';
            document.body.style.color = '#fff';
            toggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
        } else {
            // Enable light mode
            document.body.style.backgroundColor = '#f4f4f9';
            document.body.style.color = '#333';
            toggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
        }
    });
});
