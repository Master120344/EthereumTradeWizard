const fetch = require('node-fetch');
const fs = require('fs');

// Configuration for bot endpoints
const bots = [
    { name: "Ethereum Bot", endpoint: "http://localhost:3000/ethbot/performance" },
    { name: "Solana Bot", endpoint: "http://localhost:3000/solbot/performance" },
    { name: "Polkadot Bot", endpoint: "http://localhost:3000/poles/performance" },
    { name: "Matic Bot", endpoint: "http://localhost:3000/maticbot/performance" },
    { name: "Uniswap Bot", endpoint: "http://localhost:3000/uniswap/performance" },
    // Add additional bots as necessary
];

// Function to check performance metrics in real time
const checkPerformance = async () => {
    const results = [];
    const promises = bots.map(async (bot) => {
        try {
            const response = await fetch(bot.endpoint);
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();

            results.push({
                name: bot.name,
                latency: data.latency || 'N/A',
                successRate: data.successRate || 'N/A',
                lastTradeTime: data.lastTradeTime || 'N/A',
                tradeVolume: data.tradeVolume || 'N/A'
            });
        } catch (error) {
            console.error(`Error fetching performance data for ${bot.name}:`, error);
            results.push({
                name: bot.name,
                latency: 'N/A',
                successRate: 'N/A',
                lastTradeTime: 'N/A',
                tradeVolume: 'N/A'
            });
        }
    });

    await Promise.all(promises);
    return results;
};

// Function to log performance data to console and sync with a log file
const logPerformance = async (performanceData) => {
    const logEntries = [];
    
    performanceData.forEach((bot) => {
        const entry = `- ${bot.name}: Latency: ${bot.latency} ms, Success Rate: ${bot.successRate}%, Last Trade: ${bot.lastTradeTime}, Trade Volume: ${bot.tradeVolume}`;
        console.log(entry);
        logEntries.push(entry);
    });

    // Sync with log file
    fs.appendFile('performance_log.txt', logEntries.join('\n') + '\n', (err) => {
        if (err) {
            console.error("Failed to write performance log:", err);
        } else {
            console.log("Performance metrics logged successfully.");
        }
    });
};

// Function to analyze performance trends and alert if necessary
const analyzePerformance = (performanceData) => {
    const alertThreshold = 80; // Example threshold for success rate
    performanceData.forEach((bot) => {
        if (bot.successRate < alertThreshold) {
            console.warn(`ALERT: ${bot.name} has a low success rate of ${bot.successRate}%`);
        }
    });
};

// Function to run performance checks in real time
const runPerformanceChecks = async () => {
    const performanceData = await checkPerformance();
    await logPerformance(performanceData);
    analyzePerformance(performanceData);

    // Schedule next check after a defined interval
    setTimeout(runPerformanceChecks, 30000); // Check every 30 seconds
};

// Start the performance checks
runPerformanceChecks();