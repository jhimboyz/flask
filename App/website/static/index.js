(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            var spinnerElement = $('#spinner');
            if (spinnerElement.length > 0) {
                spinnerElement.removeClass('show');
            }
        }, 1);
    };

    // Call the spinner function    
    spinner();
    

    // Function to fetch distance data from the server
    function fetchDistance() {
        fetch('/distance')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();  // Parse the JSON response
            })
            .then(data => {
                // Check if distance and status are available in the data
                if (data.distance && data.status) {
                    // Update the distance and status in the DOM
                    document.getElementById('distance').textContent = `${data.distance} `;
                    document.getElementById('status').textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);

                    // Update the status class dynamically
                    const statusElement = document.getElementById('status');
                    statusElement.className = `status ${data.status}`;  // Apply new class to status
                } else {
                    console.error('Invalid data format:', data);
                }
            })
            .catch(error => {
                console.error('Error fetching distance:', error);
            });
    }

    // Fetch distance data periodically every 5 seconds
    setInterval(fetchDistance, 5000);

    // Initial fetch to populate data on page load
    fetchDistance();

})(jQuery);
