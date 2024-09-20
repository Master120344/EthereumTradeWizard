const fs = require('fs');
const path = require('path');

// Trading history directory
const historyDir = path.join(__dirname, 'trading_history');

// Create directory if it doesn't exist
if (!fs.existsSync(historyDir)) {
    fs.mkdirSync(historyDir);
}

// Trade history array to store trades
let tradeHistory = [];

// Function to log a trade
const logTrade = (botName, exchange, tradingPair, tradeDetails) => {
    const trade = {
        timestamp: new Date().toISOString(),
        botName,
        exchange,
        tradingPair,
        ...tradeDetails,
        netProfit: calculateNetProfit(tradeDetails) // Calculate net profit for the trade
    };

    tradeHistory.push(trade);
    saveTradeToFile(botName, exchange, trade);
};

// Function to calculate net profit
const calculateNetProfit = (tradeDetails) => {
    const totalCost = tradeDetails.total + tradeDetails.fee;
    return (tradeDetails.side === "sell") ? tradeDetails.total - totalCost : 0; // Only return profit for sell trades
};

// Function to save trade to a file
const saveTradeToFile = (botName, exchange, trade) => {
    const filePath = path.join(historyDir, `${botName.replace(/ /g, '_')}_${exchange}_trades.json`);

    // Read existing trades
    let existingTrades = [];
    if (fs.existsSync(filePath)) {
        const data = fs.readFileSync(filePath);
        existingTrades = JSON.parse(data);
    }

    existingTrades.push(trade);
    fs.writeFileSync(filePath, JSON.stringify(existingTrades, null, 2));
    console.log(`Trade logged for ${botName} on ${exchange}:`, trade);
};

// Function to simulate a trade execution
const executeTrade = (botName, exchange, tradingPair, amount, price, side) => {
    const tradeDetails = {
        amount,
        price,
        side,
        total: amount * price,
        fee: calculateFee(amount * price), // Calculate fee based on the total trade value
        timeExecuted: new Date().toISOString() // Add execution time
    };

    // Log the trade
    logTrade(botName, exchange, tradingPair, tradeDetails);
};

// Function to calculate fees (example: 0.1% of total trade value)
const calculateFee = (total) => {
    return total * 0.001; // 0.1% fee
};

// Example of simulated trades
const exampleTrades = [
    { botName: "Ethereum Bot", exchange: "Binance", tradingPair: "ETH/USDT", amount: 1, price: 2000, side: "buy" },
    { botName: "Solana Bot", exchange: "Kraken", tradingPair: "SOL/USDT", amount: 5, price: 50, side: "sell" },
    { botName: "Polkadot Bot", exchange: "Coinbase", tradingPair: "DOT/USDT", amount: 10, price: 10, side: "buy" },
    { botName: "Uniswap Bot", exchange: "Uniswap", tradingPair: "UNI/USDT", amount: 2, price: 30, side: "sell" },
    { botName: "Litecoin Bot", exchange: "Bittrex", tradingPair: "LTC/USDT", amount: 3, price: 150, side: "buy" },
];

// Simulate executing trades
exampleTrades.forEach(trade => {
    executeTrade(trade.botName, trade.exchange, trade.tradingPair, trade.amount, trade.price, trade.side);
});

// Function to retrieve trade history for a specific bot and exchange
const getTradeHistory = (botName, exchange) => {
    const filePath = path.join(historyDir, `${botName.replace(/ /g, '_')}_${exchange}_trades.json`);
    if (fs.existsSync(filePath)) {
        const data = fs.readFileSync(filePath);
        return JSON.parse(data);
    }
    return [];
};

// Function to generate a summary of trades
const generateTradeSummary = (botName, exchange) => {
    const history = getTradeHistory(botName, exchange);
    let totalProfit = 0;
    let totalTrades = history.length;

    history.forEach(trade => {
        totalProfit += trade.netProfit;
    });

    return {
        botName,
        exchange,
        totalTrades,
        totalProfit
    };
};

// Example of generating a summary
const summary = generateTradeSummary("Ethereum Bot", "Binance");
console.log("Trade Summary for Ethereum Bot on Binance:", summary);

// Function to clean up old trade logs based on age (e.g., older than 30 days)
const cleanOldLogs = () => {
    const now = new Date();
    fs.readdir(historyDir, (err, files) => {
        if (err) throw err;

        files.forEach(file => {
            const filePath = path.join(historyDir, file);
            const stats = fs.statSync(filePath);
            const fileAgeInDays = (now - stats.mtime) / (1000 * 60 * 60 * 24);

            if (fileAgeInDays > 30) {
                fs.unlinkSync(filePath); // Delete old log files
                console.log(`Deleted old log file: ${file}`);
            }
        });
    });
};

// Clean up old logs
cleanOldLogs();