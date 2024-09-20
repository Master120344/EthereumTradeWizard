// index.js

const initializeDashboard = async () => {
    try {
        await updateDashboard();
        setInterval(updateDashboard, 30000); // Refresh every 30 seconds
        monitorExchanges();
    } catch (error) {
        console.error("Initialization error:", error);
        alert("Initialization failed. Please check your connection.");
    }
};

// Fetch data from the API
const fetchData = async () => {
    try {
        const response = await fetch('/api/data'); // Replace with your API endpoint
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error("Fetching data failed:", error);
        throw error;
    }
};

// Update dashboard content
const updateDashboard = async () => {
    const loading = document.getElementById("loading");
    loading.style.display = "flex"; // Show loading spinner

    try {
        const data = await fetchData();
        loading.style.display = "none"; // Hide loading spinner

        updateAccountSummary(data);
        updateBotList(data.bots);
        updateTradingHistory(data.trades);
        updateVolumeChart(data.volumeData);
        monitorTradingStatus(data.bots);
    } catch (error) {
        loading.style.display = "none"; // Hide loading on error
        alert("Failed to update dashboard. Please try again.");
    }
};

// Update account summary information
const updateAccountSummary = (data) => {
    document.getElementById("current-balance").innerText = `$${data.currentBalance.toFixed(2)}`;
    document.getElementById("total-profit").innerText = `$${data.totalProfit.toFixed(2)}`;
    document.getElementById("total-trades").innerText = data.totalTrades;
};

// Update bot information
const updateBotList = (bots) => {
    const botList = document.getElementById("bot-list");
    botList.innerHTML = ""; // Clear existing bots
    bots.forEach(bot => {
        const botCard = document.createElement("div");
        botCard.className = "bot-card";
        botCard.innerHTML = `
            <h3>${bot.name}</h3>
            <p>Status: <span class="status ${bot.status.toLowerCase()}">${bot.status}</span></p>
            <p>Profit: <span class="profit">$${bot.profit.toFixed(2)}</span></p>
            <p>Last Trade: <span>${bot.lastTrade || 'N/A'}</span></p>
            <p><button onclick="executeTrade('${bot.id}')">Execute Trade</button></p>
        `;
        botList.appendChild(botCard);
    });
};

// Update trading history
const updateTradingHistory = (trades) => {
    const tradeHistory = document.getElementById("trade-history");
    tradeHistory.innerHTML = ""; // Clear existing trades
    trades.forEach(trade => {
        const tradeRow = document.createElement("div");
        tradeRow.className = "trade-row";
        tradeRow.innerHTML = `
            <div>Trade #${trade.tradeId}</div>
            <div>Amount: $${trade.amount.toFixed(2)}</div>
            <div>Fee: $${trade.fee.toFixed(2)}</div>
            <div>Exchange: ${trade.exchange}</div>
            <div>Status: <span class="${trade.status.toLowerCase()}">${trade.status}</span></div>
        `;
        tradeHistory.appendChild(tradeRow);
    });
};

// Update trading volume chart
const updateVolumeChart = (volumeData) => {
    const ctx = document.getElementById('volumeChart').getContext('2d');
    if (window.volumeChart) {
        window.volumeChart.destroy(); // Destroy previous chart instance
    }
    window.volumeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: volumeData.labels,
            datasets: [{
                label: 'Trading Volume',
                data: volumeData.values,
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
                    title: {
                        display: true,
                        text: 'Months'
                    },
                    beginAtZero: true
                },
                y: {
                    title: {
                        display: true,
                        text: 'Volume ($)'
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: true,
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ${context.dataset.label}: $${context.parsed.y}`;
                        }
                    }
                }
            }
        }
    });
};

// Execute a trade for a specific bot
const executeTrade = async (botId) => {
    try {
        const loading = document.getElementById("loading");
        loading.style.display = "flex"; // Show loading spinner
        const response = await fetch(`/api/trade/${botId}`, { method: 'POST' });
        if (!response.ok) throw new Error('Trade execution failed');

        const result = await response.json();
        alert(`Trade executed for bot ${botId}: ${result.message}`);
        loading.style.display = "none"; // Hide loading spinner
    } catch (error) {
        console.error("Trade execution error:", error);
        alert("Failed to execute trade. Please try again.");
    }
};

// Monitor trading status and update bot status dynamically
const monitorTradingStatus = (bots) => {
    bots.forEach(bot => {
        if (bot.status === "Active") {
            const statusCheck = setInterval(async () => {
                const response = await fetch(`/api/bot-status/${bot.id}`);
                const status = await response.json();
                const botCard = document.querySelector(`.bot-card h3:contains('${bot.name}')`).closest('.bot-card');
                botCard.querySelector('.status').innerText = status.status;
            }, 60000); // Check every minute
        }
    });
};

// Event listeners
document.getElementById('refreshButton').addEventListener('click', updateDashboard);

// Initial loading
initializeDashboard();