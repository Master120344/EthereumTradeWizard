document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('bot-setup-form');
    const setupProgress = document.getElementById('setup-progress');
    
    const usedBots = new Set();

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        let completed = 0;

        for (let i = 0; i < 10; i++) {
            const botSelect = document.getElementById(`bot-select-${i}`);
            const exchangeSelect = document.getElementById(`exchange-select-${i}`);
            const apiKey = document.getElementById(`api-key-${i}`).value.trim();
            const walletAddress = document.getElementById(`wallet-address-${i}`).value.trim();
            const receivingWallet = document.getElementById(`receiving-wallet-${i}`).value.trim();
            const depositAddress = document.getElementById(`deposit-address-${i}`).value.trim();

            const selectedBot = botSelect.value;
            const selectedExchange = exchangeSelect.value;

            if (selectedBot && !usedBots.has(selectedBot) && selectedExchange && apiKey && walletAddress && receivingWallet && depositAddress) {
                usedBots.add(selectedBot);
                document.getElementById(`status-${i}`).innerText = `${selectedBot} setup successfully!`;
                completed++;
            } else {
                document.getElementById(`status-${i}`).innerText = `Error: Invalid setup or bot already used.`;
            }
        }

        setupProgress.innerText = `Setup Progress: ${completed} out of 10`;
        form.reset();
    });
});