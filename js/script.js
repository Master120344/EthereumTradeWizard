// Function to simulate fetching data from an API
const fetchData = () => {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                currentBalance: 12345.67,
                totalProfit: 890.12,
                bots: [
                    { name: "Ethereum Bot 1", profit: 200.00, status: "Active" },
                    { name: "Ethereum Bot 2", profit: 150.00, status: "Active" },
                    { name: "Bitcoin Bot 1", profit: 300.00, status: "Inactive" },
                    { name: "Solana Bot 1", profit: 240.00, status: "Active" },
                    { name: "Ethereum Bot 3", profit: 180.00, status: "Active" },
                    { name: "Cardano Bot 1", profit: 220.00, status: "Inactive" },
                    { name: "Polkadot Bot 1", profit: 190.00, status: "Active" },
                    { name: "Litecoin Bot 1", profit: 170.00, status: "Active" },
                    { name: "Dogecoin Bot 1", profit: 160.00, status: "Inactive" },
                    { name: "Ripple Bot 1", profit: 210.00, status: "Active" }
                ],
                trades: [
                    { tradeId: 1, amount: 100.00, fee: 1.00, exchange: 'Binance' },
                    { tradeId: 2, amount: 150.00, fee: 1.50, exchange: 'Coinbase' },
                    { tradeId: 3, amount: 200.00, fee: 2.00, exchange: 'Kraken' }
                ]
            });
        }, 1000);
    });
};

// Function to update the dashboard
const updateDashboard = async () => {
    const loading = document.getElementById("loading");
    const botList = document.querySelector(".bot-list");
    const currentBalanceElement = document.getElementById("current-balance");
    const totalProfitElement = document.getElementById("total-profit");

    try {
        loading.style.display = "flex"; // Show loading spinner
        const data = await fetchData();

        if (!data || typeof data !== "object") {
            throw new Error("Invalid data format.");
        }

        // Hide loading spinner
        loading.style.display = "none";

        // Update balance and profit with validation
        if (typeof data.currentBalance === "number" && typeof data.totalProfit === "number") {
            currentBalanceElement.innerText = `$${data.currentBalance.toFixed(2)}`;
            totalProfitElement.innerText = `$${data.totalProfit.toFixed(2)}`;
        } else {
            currentBalanceElement.innerText = `$0.00`;
            totalProfitElement.innerText = `$0.00`;
        }

        // Update bot information
        updateBotList(data.bots);
        
    } catch (error) {
        loading.style.display = "none"; // Hide loading even on failure
        console.error("Error updating dashboard:", error);
        // Optional: Display a user-friendly message in the UI
    }
};

// Function to update the bot list
const updateBotList = (bots) => {
    const botList = document.querySelector(".bot-list");
    botList.innerHTML = ""; // Clear existing bots

    if (!Array.isArray(bots)) return;

    bots.forEach(bot => {
        const botCard = document.createElement("div");
        botCard.className = "bot-card";
        botCard.innerHTML = `
            <h3>${bot.name}</h3>
            <p>Status: <span class="status ${bot.status.toLowerCase()}">${bot.status}</span></p>
            <p>Profit: <span class="profit">$${bot.profit.toFixed(2)}</span></p>
        `;
        botList.appendChild(botCard);
    });
};

// Initial loading
document.addEventListener("DOMContentLoaded", updateDashboard);