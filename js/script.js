document.addEventListener("DOMContentLoaded", () => {
    // Simulate fetching data from an API
    const fetchData = () => {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    currentBalance: 12345.67,
                    totalProfit: 890.12,
                    bots: [
                        { name: "Ethereum Bot 1", profit: 200.00, status: "Active" },
                        { name: "Ethereum Bot 2", profit: 150.00, status: "Active" },
                        { name: "Bitcoin Bot 1", profit: 300.00, status: "Active" },
                        { name: "Solana Bot 1", profit: 240.00, status: "Active" },
                    ]
                });
            }, 1000);
        });
    };

    const updateDashboard = async () => {
        const data = await fetchData();

        // Update balance and profit
        document.getElementById("current-balance").innerText = `$${data.currentBalance.toFixed(2)}`;
        document.getElementById("total-profit").innerText = `$${data.totalProfit.toFixed(2)}`;

        // Update bot information
        const botList = document.querySelector(".bot-list");
        botList.innerHTML = ""; // Clear existing bots
        data.bots.forEach(bot => {
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
    updateDashboard();
});