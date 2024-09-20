// chart.js

document.addEventListener("DOMContentLoaded", () => {
    // Get the context of the canvas element
    const ctx = document.getElementById('volumeChart').getContext('2d');

    // Initialize the chart with improved settings
    const volumeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Labels for the x-axis
            datasets: [{
                label: 'Trading Volume',
                data: [], // Data for the chart
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                borderWidth: 2,
                fill: true,
                pointRadius: 3,
                pointHoverRadius: 5,
                pointBackgroundColor: '#3498db',
                pointBorderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        tooltipFormat: 'll HH:mm'
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    },
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 10
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Volume'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString(); // Format numbers with commas
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(tooltipItem) {
                            return `Volume: ${tooltipItem.raw.toLocaleString()}`;
                        }
                    }
                }
            }
        }
    });

    // Function to fetch real-time data
    const fetchRealTimeData = async () => {
        try {
            const response = await fetch('/api/trading-volume'); // Replace with your API endpoint
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();

            // Update chart with new data
            volumeChart.data.labels = data.labels; // Array of labels, e.g., timestamps
            volumeChart.data.datasets[0].data = data.values; // Array of values
            volumeChart.update();
        } catch (error) {
            console.error('Error fetching real-time data:', error);
        }
    };

    // Fetch initial data and set up interval for real-time updates
    fetchRealTimeData();
    setInterval(fetchRealTimeData, 60000); // Update every minute (60000 ms)

    // Optional: Set up event listener for manual refresh button if needed
    const refreshButton = document.getElementById('refreshButton');
    if (refreshButton) {
        refreshButton.addEventListener('click', fetchRealTimeData);
    }
});