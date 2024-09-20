document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('bot-setup-form');
    const botSections = document.getElementById('bot-sections');
    const setupProgress = document.getElementById('setup-progress');
    
    const bots = [
        "Ethereum Bot 1", "Ethereum Bot 2", "Bitcoin Bot 1", 
        "Solana Bot 1", "Ethereum Bot 3", "Cardano Bot 1", 
        "Polkadot Bot 1", "Litecoin Bot 1", "Dogecoin Bot 1", 
        "Ripple Bot 1"
    ];
    const exchanges = ["Binance", "Coinbase", "Kraken", "Bitfinex", "Huobi", "Bittrex", "KuCoin", "Gemini", "Gate.io", "OKEx"];
    
    const usedBots = new Set();
    const usedExchanges = new Set();
    
    for (let i = 0; i < 10; i++) {
        const section = document.createElement('div');
        section.className = 'section';
        section.innerHTML = `
            <h3>Bot Setup ${i + 1}</h3>
            <label for="bot-select-${i}">Select Bot:</label>
            <select id="bot-select-${i}">
                <option value="">Select a bot</option>
                ${bots.map(bot => `<option value="${bot}">${bot}</option>`).join('')}
            </select>
            <label for="exchange-select-${i}">Select Exchange:</label>
            <select id="exchange-select-${i}">
                <option value="">Select an exchange</option>
                ${exchanges.map(exchange => `<option value="${exchange}">${exchange}</option>`).join('')}
            </select>
            <label for="api-key-${i}">API Key:</label>
            <input type="text" id="api-key-${i}" required>
            <label for="wallet-address-${i}">Wallet Address:</label>
            <input type="text" id="wallet-address-${i}" required>
            <label for="receiving-wallet-${i}">Receiving Wallet Address:</label>
            <input type="text" id="receiving-wallet-${i}" required>
            <label for="deposit-address-${i}">Deposit Address:</label>
            <input type="text" id="deposit-address-${i}" required>
            <div class="status" id="status-${i}"></div>
        `;
        botSections.appendChild(section);
    }
    
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

            if (selectedBot && !usedBots.has(selectedBot) && selectedExchange) {
                usedBots.add(selectedBot);
                // Here you can add your setup processing logic
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