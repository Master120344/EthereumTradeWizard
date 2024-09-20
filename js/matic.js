// maticBot.js
const fetch = require('node-fetch');
const { getGasFees } = require('./gasfees'); // Import gas fee checker
const { executeTrade } = require('./tradeExecutor'); // Trade execution logic
const exchanges = require('./exchanges'); // List of exchanges

class MaticBot {
    constructor() {
        this.bestPrice = null;
        this.bestExchange = null;
        this.tradeAmount = 100; // Amount in MATIC to trade
    }

    async fetchPriceData() {
        const promises = exchanges.map(exchange => {
            return fetch(`${exchange.api}/ticker/matic`)
                .then(res => res.json())
                .then(data => ({ price: data.price, exchange: exchange.name }));
        });

        return Promise.all(promises);
    }

    async checkBestPrice(prices) {
        prices.forEach(priceData => {
            if (this.bestPrice === null || priceData.price < this.bestPrice) {
                this.bestPrice = priceData.price;
                this.bestExchange = priceData.exchange;
            }
        });
    }

    async executeTrade() {
        const gasFees = await getGasFees(); // Fetch gas fees
        if (this.bestPrice && gasFees) {
            const totalCost = this.bestPrice * this.tradeAmount + gasFees;
            console.log(`Executing trade on ${this.bestExchange} at price ${this.bestPrice}. Total cost: ${totalCost}`);
            await executeTrade(this.bestExchange, this.tradeAmount);
        } else {
            console.log('No valid trade conditions met.');
        }
    }

    async monitor() {
        while (true) {
            console.log('Checking prices...');
            const prices = await this.fetchPriceData();
            await this.checkBestPrice(prices);
            await this.executeTrade();

            // Reset best price and exchange for the next iteration
            this.bestPrice = null;
            this.bestExchange = null;

            // Sleep for a while before the next check
            await new Promise(resolve => setTimeout(resolve, 10000)); // Check every 10 seconds
        }
    }
}

// Initialize and start the Matic bot
const maticBot = new MaticBot();
maticBot.monitor();