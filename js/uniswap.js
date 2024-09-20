const Web3 = require('web3');
const fetch = require('node-fetch');
const gasFees = require('./gasFees');

const UNISWAP_API_URL = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2';
const web3 = new Web3(new Web3.providers.HttpProvider('https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'));

const fetchUniswapPrices = async (tokenAddress) => {
    const query = `
        {
            pairs(first: 5, orderBy: reserveUSD, orderDirection: desc) {
                id
                token0 {
                    id
                    symbol
                    derivedETH
                }
                token1 {
                    id
                    symbol
                    derivedETH
                }
                reserve0
                reserve1
                volumeUSD
            }
        }
    `;

    const response = await fetch(UNISWAP_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
    });

    const data = await response.json();
    return data.data.pairs.map(pair => ({
        id: pair.id,
        token0: pair.token0.symbol,
        token1: pair.token1.symbol,
        reserve0: parseFloat(pair.reserve0),
        reserve1: parseFloat(pair.reserve1),
        price: pair.token0.symbol === 'ETH' ? (pair.reserve1 / pair.reserve0) : (pair.reserve0 / pair.reserve1),
    }));
};

const findArbitrageOpportunities = async () => {
    const tokenAddress = '0x...'; // Replace with the token address you want to check
    const uniswapPrices = await fetchUniswapPrices(tokenAddress);
    
    uniswapPrices.sort((a, b) => a.price - b.price);

    const lowestPrice = uniswapPrices[0];
    const highestPrice = uniswapPrices[uniswapPrices.length - 1];

    const gasFee = await gasFees.getGasFee('Uniswap');

    if (highestPrice.price - lowestPrice.price > gasFee) {
        console.log(`Arbitrage Opportunity Detected on Uniswap!`);
        console.log(`Buy on ${lowestPrice.token0} at $${lowestPrice.price.toFixed(2)} (Gas Fee: $${gasFee})`);
        console.log(`Sell on ${highestPrice.token1} at $${highestPrice.price.toFixed(2)}`);
    } else {
        console.log(`No arbitrage opportunity found on Uniswap.`);
    }
};

const runUniswapBot = async () => {
    console.log(`Uniswap Bot is starting...`);
    setInterval(findArbitrageOpportunities, 30000); // Check every 30 seconds
};

runUniswapBot();