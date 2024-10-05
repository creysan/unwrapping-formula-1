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


// Function to populate year dropdown
function populateYears() {
    fetch('/get_years')
    .then(response => response.json())
    .then(years => {
        const yearDropdown = document.getElementById('year');
        yearDropdown.innerHTML = '';  // Clear existing options

        years.forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.text = year;
            yearDropdown.add(option);
        });

        // Trigger event to load events for the first year in the list
        yearDropdown.dispatchEvent(new Event('change'));
    })
    .catch(error => {
        console.error('Error fetching years:', error);
    });
}

// Function to populate event dropdown based on selected year
function populateEvents(year) {
    fetch(`/get_events?year=${year}`)
    .then(response => response.json())
    .then(events => {
        console.log(events);  // Log the received events
        const eventDropdown = document.getElementById('event');
        eventDropdown.innerHTML = '';  // Clear existing options

        events.forEach(event => {
            const option = document.createElement('option');
            option.value = event.round;
            option.text = event.name;
            eventDropdown.add(option);
        });

        // Trigger event to load drivers for the first event in the list
        eventDropdown.dispatchEvent(new Event('change'));
    })
    .catch(error => {
        console.error('Error fetching events:', error);
    });
}

// Function to populate drivers dropdown based on selected event
function populateDrivers(year, round) {
    // Show the loading GIF
    document.getElementById('loading').style.display = 'flex';

    fetch(`/get_drivers?year=${year}&round=${round}`)
        .then(response => response.json())
        .then(drivers => {
            console.log(drivers)
            const driversDropdown = document.getElementById('drivers');
            driversDropdown.innerHTML = '';  // Clear existing options

            drivers.forEach(driver => {
                const option = document.createElement('option');
                option.value = driver.driverId;
                option.text = driver.driverName;
                option.abbrev = driver.driverAbbreviation;
                driversDropdown.add(option);
            });
        })
        .catch(error => {
            console.error('Error fetching drivers:', error);
        })
        .finally(() => {
            // Hide the loading GIF
            document.getElementById('loading').style.display = 'none';
        });
}


// Fetch and populate the list of years when the page loads
document.addEventListener('DOMContentLoaded', populateYears);

document.addEventListener('DOMContentLoaded', () => {
    const yearDropdown = document.getElementById('year');
    if (yearDropdown) {  // Ensure the element exists
        yearDropdown.addEventListener('change', function(event) {
            const year = event.target.value;
            populateEvents(year);
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const yearDropdown = document.getElementById('year');
    const eventDropdown = document.getElementById('event');

    // Ensure both dropdowns exist before attaching event listeners
    if (yearDropdown && eventDropdown) {
        // Event listener for year dropdown
        yearDropdown.addEventListener('change', function(event) {
            const year = event.target.value;
            const round = eventDropdown.value; // Get current selected event
            populateDrivers(year, round);
        });

        // Event listener for event dropdown
        eventDropdown.addEventListener('change', function(event) {
            const year = yearDropdown.value; // Get current selected year
            const round = event.target.value;
            populateDrivers(year, round);
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const raceForm = document.getElementById('raceForm');
    if (raceForm) {
        raceForm.addEventListener('submit', function(event) {
            event.preventDefault();

            const year = document.getElementById('year').value;
            const round = document.getElementById('event').value;
            const selectedDrivers = [...document.getElementById('drivers').selectedOptions].map(option => option.abbrev);
            const isDarkMode = localStorage.getItem('darkMode') === 'true';
            const loadingElement = document.getElementById('loading');

            // Show the loading logo
            loadingElement.style.display = 'flex';

            // Assuming selectedDrivers is an array of driver abbreviations
            const driverAbbrv = selectedDrivers[0];  // Assuming you are selecting only one driver

            fetch(`/get_race_data?year=${year}&round=${round}&drivers=${encodeURIComponent(driverAbbrv)}`)
            .then(response => response.json())
            .then(data => {
                // Hide the loading logo
                loadingElement.style.display = 'none';

                // Plotly plot
                const plotlyDiv = document.getElementById('plotly-div');
                plotlyDiv.style.display = 'block';
                const plotlyData = JSON.parse(data.plotly_json);
                Plotly.newPlot('plotly-div', plotlyData.data, plotlyData.layout);

                // Hide the static image plot (if any)
                const imgElement = document.getElementById('raceGraph');
                imgElement.style.display = 'none';

                const fastestLapElement = document.getElementById('fastestLap');
                // Handle exceptional_laps data if needed
                fastestLapElement.style.display = 'block';
            })
            .catch(error => {
                // Hide the loading logo even if there is an error
                loadingElement.style.display = 'none';
                console.error('Error fetching race data:', error);
            });
        });
    }
});



// Function to convert seconds to 'MM:SS' format
function seconds_to_minutes(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

document.addEventListener('DOMContentLoaded', function() {
    const predictionForm = document.getElementById('predictionForm');
    const yearSelect = document.getElementById('year');
    const eventSelect = document.getElementById('event');
    const predictionTable = document.getElementById('predictionTable');
    const loadingIndicator = document.getElementById('loading');

    predictionForm.addEventListener('submit', function(e) {
        e.preventDefault(); // Prevent form submission

        // Show loading indicator
        loadingIndicator.style.display = 'block';
        
        // Hide previous results
        predictionTable.style.display = 'none';
        
        const year = yearSelect.value;
        const event = eventSelect.value;
        
        if (!year || !event) {
            alert('Please select both year and event.');
            loadingIndicator.style.display = 'none';
            return;
        }

        fetch('/predict_winner', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ year: year, event: event }),
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.style.display = 'none';
            
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                const tableBody = predictionTable.querySelector('tbody');
                tableBody.innerHTML = ''; // Clear previous results
                
                data.predicted_winners.forEach((winner, index) => {
                    const row = tableBody.insertRow();
                    const positionCell = row.insertCell(0);
                    const driverCell = row.insertCell(1);
                    const probabilityCell = row.insertCell(2);
                    
                    positionCell.textContent = index + 1;
                    driverCell.textContent = winner.driver;
                    probabilityCell.textContent = (winner.probability * 100).toFixed(2) + '%';
                });
                
                // Show the table
                predictionTable.style.display = 'table';
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while fetching the prediction.');
            loadingIndicator.style.display = 'none';
        });
    });
});
