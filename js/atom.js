const fetch = require('node-fetch');
const exchanges = require('./exchanges'); // Ensure this imports your exchange data
const gasFees = require('./gasFees');

const ATOM_BOT_NAME = 'Cosmos Bot';

const fetchATOMPrices = async () => {
    const pricePromises = exchanges.map(async (exchange) => {
        const response = await fetch(`${exchange.api}/price?symbol=ATOM`);
        const data = await response.json();
        return { exchange: exchange.name, price: data.price, gasFee: await gasFees.getGasFee(exchange) };
    });

    return Promise.all(pricePromises);
};

const findArbitrageOpportunities = async () => {
    const atomPrices = await fetchATOMPrices();
    atomPrices.sort((a, b) => a.price - b.price);

    const lowestPrice = atomPrices[0];
    const highestPrice = atomPrices[atomPrices.length - 1];

    if (highestPrice.price - lowestPrice.price > 0) {
        console.log(`Arbitrage Opportunity Detected for ${ATOM_BOT_NAME}!`);
        console.log(`Buy on ${lowestPrice.exchange} at $${lowestPrice.price} with gas fee $${lowestPrice.gasFee}`);
        console.log(`Sell on ${highestPrice.exchange} at $${highestPrice.price}`);
    } else {
        console.log(`No arbitrage opportunity found for ${ATOM_BOT_NAME}.`);
    }
};

const runAtomBot = async () => {
    console.log(`${ATOM_BOT_NAME} is starting...`);
    setInterval(findArbitrageOpportunities, 30000); // Check every 30 seconds
};

runAtomBot();