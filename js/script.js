const updateDashboard = async () => {
    const loading = document.getElementById("loading");
    loading.style.display = "flex"; // Show loading spinner

    const data = await fetchData();
    
    loading.style.display = "none"; // Hide loading spinner

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