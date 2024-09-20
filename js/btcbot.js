const axios = require('axios');
const gasFees = require('./gasFees');
const exchanges = require('./exchanges'); // Assume exchanges.js exports a function to get exchange data

const BTC_THRESHOLD = 0.001; // Minimum profit threshold for executing trades
const TRADE_AMOUNT = 0.01; // Amount to trade in BTC

const checkArbitrageOpportunity = async () => {
    try {
        const gasFeeData = await gasFees.findCheapestGasFee('BTC');
        const exchangeData = await exchanges.getExchangeData('BTC'); // Fetch current prices from all exchanges

        // Compare prices to find arbitrage opportunities
        let highestProfit = 0;
        let bestExchangeBuy, bestExchangeSell;

        for (const buyExchange of exchangeData) {
            for (const sellExchange of exchangeData) {
                if (buyExchange.name === sellExchange.name) continue;

                const potentialProfit = (sellExchange.price - buyExchange.price) * TRADE_AMOUNT - gasFeeData.fee;

                if (potentialProfit > highestProfit && potentialProfit > BTC_THRESHOLD) {
                    highestProfit = potentialProfit;
                    bestExchangeBuy = buyExchange;
                    bestExchangeSell = sellExchange;
                }
            }
        }

        if (highestProfit > 0) {
            console.log(`Arbitrage Opportunity Found! Buy from ${bestExchangeBuy.name} and sell to ${bestExchangeSell.name} with profit: $${highestProfit.toFixed(2)}`);
            await executeTrade(bestExchangeBuy, bestExchangeSell, TRADE_AMOUNT);
        } else {
            console.log("No profitable arbitrage opportunities found.");
        }
    } catch (error) {
        console.error("Error checking arbitrage opportunities:", error);
    }
};

const executeTrade = async (buyExchange, sellExchange, amount) => {
    try {
        // Execute buy order on the buyExchange
        console.log(`Buying ${amount} BTC from ${buyExchange.name}`);
        // Add API call to buy from the exchange
        await buyExchange.executeOrder('buy', amount);

        // Execute sell order on the sellExchange
        console.log(`Selling ${amount} BTC to ${sellExchange.name}`);
        // Add API call to sell to the exchange
        await sellExchange.executeOrder('sell', amount);

        console.log(`Trade executed successfully between ${buyExchange.name} and ${sellExchange.name}`);
    } catch (error) {
        console.error("Error executing trade:", error);
    }
};

// Monitor for arbitrage opportunities at defined intervals
const monitorArbitrage = (interval) => {
    setInterval(checkArbitrageOpportunity, interval);
};

// Start monitoring for arbitrage opportunities every minute
monitorArbitrage(60000);