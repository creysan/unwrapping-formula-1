// Light and dark mode functionality.
document.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const lightModeCSS = document.getElementById('light-mode-css');
    const darkModeCSS = document.getElementById('dark-mode-css');
  
    // Function to apply the theme
    const applyTheme = (isDark) => {
        if (isDark) {
            lightModeCSS.setAttribute('media', 'none');
            lightModeCSS.setAttribute('disabled', 'disabled');
            darkModeCSS.removeAttribute('media');
            darkModeCSS.removeAttribute('disabled');
            document.body.classList.add('dark-mode');
        } else {
            darkModeCSS.setAttribute('media', 'none');
            darkModeCSS.setAttribute('disabled', 'disabled');
            lightModeCSS.removeAttribute('media');
            lightModeCSS.removeAttribute('disabled');
            document.body.classList.remove('dark-mode');
        }
    };
  
    // Event listener for the toggle switch
    darkModeToggle.addEventListener('change', function () {
        const isDark = this.checked;
        applyTheme(isDark);
        // Save the preference to localStorage
        localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
    });
  
    // On page load, check localStorage and apply the saved theme
    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme === 'enabled') {
        darkModeToggle.checked = true;
        applyTheme(true);
    } else {
        darkModeToggle.checked = false;
        applyTheme(false);
    }
  });
  
  
  // Add class navbarDark on navbar scroll
  const header = document.querySelector('.navbar');
  
  window.onscroll = function() {
      var top = window.scrollY;
      if (top >= 965) {
          header.classList.add('navbarDark');
      }
      else {
          header.classList.remove('navbarDark');
      }
  }
