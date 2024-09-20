document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('botSetupForm');
    const botSelect = document.getElementById('exchange');
    const usedBotList = document.getElementById('used-bot-list');

    const usedBots = new Set();

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const selectedBot = botSelect.value;

        // Validation
        if (!selectedBot || usedBots.has(selectedBot)) {
            alert('Please select a valid bot that has not been used yet.');
            return;
        }

        const exchange = form.elements['exchange'].value.trim();
        const apiKey = form.elements['apiKey'].value.trim();
        const walletAddress = form.elements['walletAddress'].value.trim();

        if (!exchange || !apiKey || !walletAddress) {
            alert('Please fill in all required fields.');
            return;
        }

        // Optional fields check
        const apiSecret = form.elements['apiSecret'] ? form.elements['apiSecret'].value.trim() : '';
        const seedPhrase = form.elements['seedPhrase'] ? form.elements['seedPhrase'].value.trim() : '';

        // Create a list item for the used bot
        const listItem = document.createElement('li');
        listItem.textContent = selectedBot;
        usedBotList.appendChild(listItem);

        // Process the setup (e.g., send data to server)
        const setupData = {
            botName: selectedBot,
            exchange,
            apiKey,
            apiSecret: apiSecret || 'Not provided',
            seedPhrase: seedPhrase || 'Not provided',
            walletAddress
        };

        // Simulated setup process (replace with actual API call)
        console.log('Setting up bot with the following details:', setupData);
        
        // Show success message
        alert(`${selectedBot} has been set up successfully!`);

        // Reset the form
        form.reset();

        // Disable the selected bot
        disableBotOption(selectedBot);
    });

    // Function to disable the selected bot option
    function disableBotOption(botName) {
        const option = Array.from(botSelect.options).find(opt => opt.value === botName);
        if (option) {
            option.disabled = true;
            option.style.display = 'none'; // Hide the option
        }
    }

    // Additional features for user feedback
    botSelect.addEventListener('change', () => {
        const selectedBot = botSelect.value;
        if (usedBots.has(selectedBot)) {
            alert(`${selectedBot} has already been selected.`);
        }
    });
});