const axios = require('axios');
const gasFees = require('./gasFees');
const exchanges = require('./exchanges');

const DOT_THRESHOLD = 0.02; // Minimum profit threshold for executing trades
const TRADE_AMOUNT = 100; // Amount to trade in DOT

const checkArbitrageOpportunity = async () => {
    try {
        const gasFeeData = await gasFees.findCheapestGasFee('DOT');
        const exchangeData = await exchanges.getExchangeData('DOT'); // Fetch current prices from all exchanges

        let highestProfit = 0;
        let bestExchangeBuy, bestExchangeSell;

        for (const buyExchange of exchangeData) {
            for (const sellExchange of exchangeData) {
                if (buyExchange.name === sellExchange.name) continue;

                const potentialProfit = (sellExchange.price - buyExchange.price) * TRADE_AMOUNT - gasFeeData.fee;

                if (potentialProfit > highestProfit && potentialProfit > DOT_THRESHOLD) {
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
        console.log(`Buying ${amount} DOT from ${buyExchange.name}`);
        await buyExchange.executeOrder('buy', amount); // Placeholder for actual buy order

        console.log(`Selling ${amount} DOT to ${sellExchange.name}`);
        await sellExchange.executeOrder('sell', amount); // Placeholder for actual sell order

        console.log("Trade executed successfully!");
    } catch (error) {
        console.error("Error executing trades:", error);
    }
};

// Schedule to check for arbitrage opportunities at regular intervals
setInterval(checkArbitrageOpportunity, 30000); // Check every 30 seconds