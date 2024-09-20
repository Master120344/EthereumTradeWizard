const axios = require('axios');
const { EXCHANGES } = require('./exchanges');
const { calculateGasFees } = require('./gasFees'); // Assuming a gas fee calculation module

class EthBot {
    constructor() {
        this.bestPrice = Infinity;
        this.bestExchange = '';
        this.executionThreshold = 0.01; // Minimum profit threshold to execute trades
    }

    async fetchPrices() {
        const pricePromises = EXCHANGES.map(exchange => 
            axios.get(exchange.url)
                .then(response => this.parsePrice(response.data, exchange.name))
                .catch(error => {
                    console.error(`Error fetching from ${exchange.name}:`, error.message);
                    return null;
                })
        );

        const prices = await Promise.all(pricePromises);
        return prices.filter(price => price !== null);
    }

    parsePrice(data, exchangeName) {
        // Extract price based on exchange's response structure
        switch (exchangeName) {
            case 'Binance':
                return { exchange: exchangeName, price: parseFloat(data.price) };
            case 'Coinbase':
                return { exchange: exchangeName, price: parseFloat(data.data.amount) };
            case 'Kraken':
                return { exchange: exchangeName, price: parseFloat(data.result.ETHUSD.c[0]) };
            case 'Bitfinex':
                return { exchange: exchangeName, price: parseFloat(data[0][1]) };
            case 'Huobi':
                return { exchange: exchangeName, price: parseFloat(data.tick.close) };
            case 'KuCoin':
                return { exchange: exchangeName, price: parseFloat(data.data.price) };
            case 'Bittrex':
                return { exchange: exchangeName, price: parseFloat(data.result.lastTradeRate) };
            case 'Gate.io':
                return { exchange: exchangeName, price: parseFloat(data.result.last) };
            case 'Poloniex':
                return { exchange: exchangeName, price: parseFloat(data.ETH_USD.last) };
            case 'Bitstamp':
                return { exchange: exchangeName, price: parseFloat(data.last) };
            default:
                return null;
        }
    }

    async findBestPrice() {
        const prices = await this.fetchPrices();

        prices.forEach(({ exchange, price }) => {
            if (price < this.bestPrice) {
                this.bestPrice = price;
                this.bestExchange = exchange;
            }
        });

        console.log(`Best price found: ${this.bestPrice} on ${this.bestExchange}`);
    }

    async executeTrade(amount) {
        const gasFee = await calculateGasFees(); // Assuming this function returns gas fee
        const totalCost = this.bestPrice * amount + gasFee;

        if (totalCost > this.executionThreshold) {
            console.log(`Executing trade on ${this.bestExchange} for amount: ${amount}`);
            // Add trade execution logic here
        } else {
            console.log(`Trade not executed. Total cost below threshold: ${totalCost}`);
        }
    }

    async run(amount) {
        await this.findBestPrice();
        await this.executeTrade(amount);
    }
}

// Example usage
const ethBot = new EthBot();
ethBot.run(1); // Execute trade for 1 ETH