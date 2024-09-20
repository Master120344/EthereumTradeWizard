let tradeData = [];
let tradeLabels = [];

// Function to fetch trade data
const fetchTradeData = async () => {
    // Simulate fetching data from an API
    return new Promise((resolve) => {
        setTimeout(() => {
            const newTradeVolume = Math.floor(Math.random() * 100); // Simulated trade volume
            const timestamp = new Date().toLocaleTimeString();

            // Update trade data
            tradeData.push(newTradeVolume);
            tradeLabels.push(timestamp);

            // Keep the arrays length fixed to 12
            if (tradeData.length > 12) {
                tradeData.shift();
                tradeLabels.shift();
            }

            resolve({ tradeData, tradeLabels });
        }, 2000); // Simulate 2-second intervals
    });
};

// Function to update the live chart
const updateLiveChart = (tradeData, tradeLabels) => {
    const ctx = document.getElementById('liveChart').getContext('2d');
    if (window.liveChart) {
        window.liveChart.data.datasets[0].data = tradeData;
        window.liveChart.data.labels = tradeLabels;
        window.liveChart.update();
    } else {
        // Create the chart if it doesn't exist
        window.liveChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: tradeLabels,
                datasets: [{
                    label: 'Live Trade Volume',
                    data: tradeData,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.2)',
                    borderWidth: 2,
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                    },
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });
    }
};

// Function to refresh trade data and update the chart
const refreshLiveChart = async () => {
    try {
        const { tradeData, tradeLabels } = await fetchTradeData();
        updateLiveChart(tradeData, tradeLabels);
    } catch (error) {
        console.error("Error refreshing live chart:", error);
    }
};

// Start refreshing the live chart every 2 seconds
setInterval(refreshLiveChart, 2000);

// Initial call to set up the live chart
refreshLiveChart();