const axios = require('axios');
const gasFees = require('./gasFees');
const exchanges = require('./exchanges');

const ADA_THRESHOLD = 0.02; // Minimum profit threshold for executing trades
const TRADE_AMOUNT = 100; // Amount to trade in ADA

const checkArbitrageOpportunity = async () => {
    try {
        const gasFeeData = await gasFees.findCheapestGasFee('ADA');
        const exchangeData = await exchanges.getExchangeData('ADA'); // Fetch current prices from all exchanges

        let highestProfit = 0;
        let bestExchangeBuy, bestExchangeSell;

        for (const buyExchange of exchangeData) {
            for (const sellExchange of exchangeData) {
                if (buyExchange.name === sellExchange.name) continue;

                const potentialProfit = (sellExchange.price - buyExchange.price) * TRADE_AMOUNT - gasFeeData.fee;

                if (potentialProfit > highestProfit && potentialProfit > ADA_THRESHOLD) {
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
        console.log(`Buying ${amount} ADA from ${buyExchange.name}`);
        // Placeholder for actual API call to buy from the exchange
        await buyExchange.executeOrder('buy', amount);

        // Execute sell order on the sellExchange
        console.log(`Selling ${amount} ADA to ${sellExchange.name}`);
        // Placeholder for actual API call to sell to the exchange
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