const fs = require('fs');
const path = require('path');
const archiver = require('archiver');

// Example bot configurations
const bots = [
    { name: "Ethereum Bot", exchanges: ["Binance", "Coinbase", "Kraken"], tradingFee: 0.001 },
    { name: "Solana Bot", exchanges: ["FTX", "Kraken", "Binance"], tradingFee: 0.002 },
    { name: "Polkadot Bot", exchanges: ["Binance", "Huobi", "Coinbase"], tradingFee: 0.0015 },
    { name: "Matic Bot", exchanges: ["Binance", "Coinbase", "SushiSwap"], tradingFee: 0.001 },
    { name: "Atom Bot", exchanges: ["Binance", "Kraken", "Coinbase"], tradingFee: 0.001 },
    { name: "Uniswap Bot", exchanges: ["Uniswap", "SushiSwap"], tradingFee: 0.002 },
    // Add more bots as necessary
];

const tradingPairs = [
    { pair: "ETH/USDT", minTradeAmount: 0.01, maxTradeAmount: 10 },
    { pair: "SOL/USDT", minTradeAmount: 0.01, maxTradeAmount: 20 },
    { pair: "DOT/USDT", minTradeAmount: 0.01, maxTradeAmount: 15 },
    { pair: "MATIC/USDT", minTradeAmount: 0.01, maxTradeAmount: 10 },
    { pair: "ATOM/USDT", minTradeAmount: 0.01, maxTradeAmount: 25 },
    { pair: "UNI/USDT", minTradeAmount: 0.01, maxTradeAmount: 10 },
    // Add more trading pairs as necessary
];

// Generate contracts
const generateContracts = () => {
    const contractsDir = path.join(__dirname, 'contracts');

    // Create contracts directory if it doesn't exist
    if (!fs.existsSync(contractsDir)) {
        fs.mkdirSync(contractsDir);
    }

    bots.forEach(bot => {
        bot.exchanges.forEach(exchange => {
            const contract = {
                botName: bot.name,
                exchange: exchange,
                tradingPairs: tradingPairs.map(pair => ({
                    pair: pair.pair,
                    minTradeAmount: pair.minTradeAmount,
                    maxTradeAmount: pair.maxTradeAmount,
                    fee: bot.tradingFee,
                    executionSettings: {
                        gasLimit: 21000,
                        gasPrice: "auto",
                        slippage: 0.01 // 1% slippage tolerance
                    }
                })),
                riskManagement: {
                    stopLoss: 0.02, // 2% stop loss
                    takeProfit: 0.05, // 5% take profit
                    maxOpenTrades: 5
                },
                logging: {
                    enabled: true,
                    level: "info", // logging levels: error, warn, info, debug
                    filePath: path.join(contractsDir, `${bot.name.replace(/ /g, '_')}_${exchange}_log.txt`)
                },
                notifications: {
                    email: "user@example.com",
                    sms: "+1234567890",
                    enabled: true
                }
            };

            // Save contract to a JSON file
            const filePath = path.join(contractsDir, `${bot.name.replace(/ /g, '_')}_${exchange}.json`);
            fs.writeFileSync(filePath, JSON.stringify(contract, null, 2));
            console.log(`Contract generated for ${bot.name} on ${exchange}: ${filePath}`);
        });
    });
};

// Zip contracts
const zipContracts = () => {
    const output = fs.createWriteStream(path.join(__dirname, 'contracts.zip'));
    const archive = archiver('zip', { zlib: { level: 9 } });

    output.on('close', () => {
        console.log(`Created zip file with ${archive.pointer()} total bytes.`);
    });

    archive.pipe(output);
    archive.directory(path.join(__dirname, 'contracts'), false);
    archive.finalize();
};

// Run contract generation and zipping
generateContracts();
zipContracts();