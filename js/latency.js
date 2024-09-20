const axios = require('axios');
const exchanges = require('./exchanges'); // Import exchange configurations

// Function to measure latency for a given exchange
const measureLatency = async (exchange) => {
    const startTime = Date.now();
    const url = exchange.apiUrl; // URL to ping for latency measurement

    try {
        const response = await axios.get(url, {
            headers: {
                'X-MBX-APIKEY': exchange.apiKey // Adjust headers as necessary
            },
            timeout: 2000 // Request timeout
        });
        const latency = Date.now() - startTime;
        return { exchange: exchange.name, latency, status: response.status };
    } catch (error) {
        return { exchange: exchange.name, latency: null, error: error.message };
    }
};

// Function to execute latency tests for all exchanges
const testLatencies = async () => {
    const latencyPromises = exchanges.map(measureLatency);
    const results = await Promise.all(latencyPromises);

    // Filter and sort results
    const validResults = results.filter(result => result.latency !== null);
    validResults.sort((a, b) => a.latency - b.latency);

    console.log("Latency Results (sorted):");
    validResults.forEach(result => {
        console.log(`${result.exchange}: ${result.latency} ms`);
    });

    // Trigger optimization based on results
    optimizeTrading(validResults);
};

// Function to optimize trading strategies based on latency
const optimizeTrading = (latencyResults) => {
    latencyResults.forEach(result => {
        if (result.latency < 100) {
            console.log(`Excellent latency for ${result.exchange}: ${result.latency} ms. Optimize trades here.`);
            // Add logic to optimize trading strategies
        } else if (result.latency > 500) {
            console.warn(`High latency for ${result.exchange}: ${result.latency} ms. Consider reducing trade frequency.`);
            // Adjust trading strategies
        }
    });
};

// Run latency tests
testLatencies();