let tradingVolumeData = [];

// Function to fetch trading volume data
const fetchTradingVolumeData = async () => {
    // Simulate fetching data from an API
    return new Promise((resolve) => {
        setTimeout(() => {
            const newVolume = Math.floor(Math.random() * 2000); // Simulated new volume data
            tradingVolumeData.push(newVolume);

            // Keep the array length fixed to 12 months
            if (tradingVolumeData.length > 12) {
                tradingVolumeData.shift(); // Remove the oldest data point
            }

            resolve(tradingVolumeData);
        }, 1000);
    });
};

// Function to update the trading volume chart
const updateTradingVolumeChart = (volumeData) => {
    const ctx = document.getElementById('volumeChart').getContext('2d');
    if (window.volumeChart) {
        window.volumeChart.data.datasets[0].data = volumeData;
        window.volumeChart.update();
    }
};

// Function to refresh trading volume data and update the chart
const refreshTradingVolume = async () => {
    try {
        const volumeData = await fetchTradingVolumeData();
        updateTradingVolumeChart(volumeData);
    } catch (error) {
        console.error("Error refreshing trading volume:", error);
    }
};

// Start refreshing the trading volume every 5 seconds
setInterval(refreshTradingVolume, 5000);

// Initial call to set up the trading volume chart
refreshTradingVolume();