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
        if (data.currentBalance && data.totalProfit) {
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