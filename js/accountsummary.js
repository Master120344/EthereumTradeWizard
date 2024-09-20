const accountSummaryData = {
    currentBalance: 0,
    totalProfit: 0,
    totalTrades: 0,
    tradingVolume: []
};

// Function to fetch data
const fetchAccountSummaryData = async () => {
    // Simulate fetching data from an API
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                currentBalance: Math.random() * 10000, // Random balance for demo
                totalProfit: Math.random() * 1000, // Random profit for demo
                totalTrades: Math.floor(Math.random() * 100), // Random trades for demo
                tradingVolume: Array.from({ length: 12 }, () => Math.floor(Math.random() * 2000)) // Random volume for demo
            });
        }, 1000);
    });
};

// Function to update the summary
const updateAccountSummary = async () => {
    try {
        const data = await fetchAccountSummaryData();
        accountSummaryData.currentBalance = data.currentBalance;
        accountSummaryData.totalProfit = data.totalProfit;
        accountSummaryData.totalTrades = data.totalTrades;
        accountSummaryData.tradingVolume = data.tradingVolume;

        // Update UI elements
        document.getElementById("current-balance").innerText = `$${accountSummaryData.currentBalance.toFixed(2)}`;
        document.getElementById("total-profit").innerText = `$${accountSummaryData.totalProfit.toFixed(2)}`;
        document.getElementById("total-trades").innerText = accountSummaryData.totalTrades;

        // Update the chart with new trading volume data
        updateVolumeChart(accountSummaryData.tradingVolume);
    } catch (error) {
        console.error("Error updating account summary:", error);
    }
};

// Function to update the trading volume chart
const updateVolumeChart = (tradingVolume) => {
    const ctx = document.getElementById('volumeChart').getContext('2d');
    if (window.volumeChart) {
        window.volumeChart.data.datasets[0].data = tradingVolume;
        window.volumeChart.update();
    } else {
        window.volumeChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Trading Volume',
                    data: tradingVolume,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    borderWidth: 2,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
};

// Start updating the account summary every 5 seconds
setInterval(updateAccountSummary, 5000);

// Initial call to set up the account summary
updateAccountSummary();