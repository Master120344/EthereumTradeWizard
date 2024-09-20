const fs = require('fs');
const path = require('path');

// Path to the slippage log file
const slippageLogFile = path.join(__dirname, 'slippage_log.json');

// Initialize log file if it does not exist
if (!fs.existsSync(slippageLogFile)) {
    fs.writeFileSync(slippageLogFile, JSON.stringify([]));
}

// Function to read slippage logs from file
const readSlippageLogs = () => {
    const data = fs.readFileSync(slippageLogFile);
    return JSON.parse(data);
};

// Function to save slippage logs to file
const saveSlippageLog = (logEntry) => {
    const logs = readSlippageLogs();
    logs.push(logEntry);
    fs.writeFileSync(slippageLogFile, JSON.stringify(logs, null, 2));
};

// Function to calculate slippage
const calculateSlippage = (expectedPrice, executedPrice) => {
    return ((executedPrice - expectedPrice) / expectedPrice) * 100; // Percentage slippage
};

// Function to log slippage for a trade
const logSlippage = (botName, exchange, tradingPair, expectedPrice, executedPrice) => {
    const slippage = calculateSlippage(expectedPrice, executedPrice);
    const logEntry = {
        botName,
        exchange,
        tradingPair,
        expectedPrice,
        executedPrice,
        slippage,
        time: new Date().toISOString()
    };
    
    saveSlippageLog(logEntry);
    console.log(`Logged slippage for ${tradingPair} on ${exchange}: ${slippage.toFixed(2)}%`);
};

// Example function to simulate a trade
const executeTrade = (botName, exchange, tradingPair, amount, expectedPrice) => {
    // Simulate getting executed price (could be from an API)
    const executedPrice = expectedPrice * (1 + (Math.random() * 0.04 - 0.02)); // Simulating slippage of +/- 2%
    
    // Log the slippage
    logSlippage(botName, exchange, tradingPair, expectedPrice, executedPrice);
    
    // Additional trade execution logic here
};

// Example trades to simulate
const exampleTrades = [
    { botName: "Ethereum Bot", exchange: "Binance", tradingPair: "ETH/USDT", amount: 1, expectedPrice: 2000 },
    { botName: "Solana Bot", exchange: "Kraken", tradingPair: "SOL/USDT", amount: 5, expectedPrice: 50 },
];

exampleTrades.forEach(trade => {
    executeTrade(trade.botName, trade.exchange, trade.tradingPair, trade.amount, trade.expectedPrice);
});

// Function to get slippage logs
const getSlippageLogs = () => {
    const logs = readSlippageLogs();
    return logs;
};

// Example of fetching slippage logs
console.log("Slippage Logs:", getSlippageLogs());