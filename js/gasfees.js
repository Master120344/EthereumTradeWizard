const axios = require('axios');

const GAS_FEE_APIS = [
    {
        name: 'Etherscan',
        url: (currency) => `https://api.etherscan.io/api?module=proxy&action=eth_gasPrice&apikey=YOUR_ETHERSCAN_API_KEY`,
        parse: (data) => parseFloat(data.result) / 1e18 // Convert from wei to ether
    },
    {
        name: 'Gas Station',
        url: () => 'https://ethgasstation.info/api/ethgasAPI.json?apiKey=YOUR_GAS_STATION_API_KEY',
        parse: (data) => data.fast / 10 // Convert from Gwei to Ether
    },
    {
        name: 'Blocknative',
        url: () => 'https://api.blocknative.com/v0/gasprices/blockprices',
        parse: (data) => data.blockPrices[0].estimatedGasPrice / 1e18 // Convert from wei to ether
    }
];

const gasFeeCache = {};
const CACHE_DURATION = 60000; // Cache duration in milliseconds (1 minute)

const fetchGasFees = async (currency) => {
    const currentTime = Date.now();

    // Check cache
    if (gasFeeCache[currency] && currentTime - gasFeeCache[currency].timestamp < CACHE_DURATION) {
        console.log('Using cached gas fees for', currency);
        return gasFeeCache[currency].fees;
    }

    const gasFees = await Promise.all(GAS_FEE_APIS.map(async (api) => {
        try {
            const response = await axios.get(api.url(currency));
            const fee = api.parse(response.data);
            return { source: api.name, fee };
        } catch (error) {
            console.error(`Error fetching from ${api.name}:`, error);
            return { source: api.name, fee: Infinity }; // Return a high fee if there's an error
        }
    }));

    // Update cache
    gasFeeCache[currency] = { timestamp: currentTime, fees: gasFees };
    return gasFees;
};

const findCheapestGasFee = async (currency) => {
    const gasFees = await fetchGasFees(currency);
    const cheapest = gasFees.reduce((prev, curr) => (prev.fee < curr.fee ? prev : curr));

    console.log(`Cheapest Gas Fee for ${currency}:`, cheapest);
    return cheapest;
};

const monitorGasFees = (currency, interval) => {
    setInterval(async () => {
        await findCheapestGasFee(currency);
    }, interval);
};

// Call this function to get the cheapest gas fee for a specific currency
findCheapestGasFee('ETH');
monitorGasFees('ETH', 30000); // Monitor every 30 seconds