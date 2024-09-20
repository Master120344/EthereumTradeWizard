const exchanges = [
    { name: 'Binance', url: 'https://api.binance.com/api/v3/ticker/24hr' },
    { name: 'Coinbase', url: 'https://api.coinbase.com/v2/prices/spot?currency=USD' },
    { name: 'Kraken', url: 'https://api.kraken.com/0/public/Ticker?pair=XBTUSD' },
    { name: 'Bitfinex', url: 'https://api.bitfinex.com/v1/pubticker/btcusd' },
    { name: 'Bittrex', url: 'https://api.bittrex.com/api/v1.1/public/getmarketsummaries' },
    { name: 'Huobi', url: 'https://api.huobi.pro/market/tickers' },
    { name: 'KuCoin', url: 'https://api.kucoin.com/api/v1/market/allTickers' },
    { name: 'Gemini', url: 'https://api.gemini.com/v1/pubticker/btcusd' },
    { name: 'Poloniex', url: 'https://poloniex.com/public?command=returnTicker' },
    { name: 'OKEx', url: 'https://www.okex.com/api/v5/market/tickers' },
    // Add more exchanges as needed
];

// Function to fetch data from all exchanges
const fetchExchangeData = async () => {
    const results = await Promise.all(
        exchanges.map(async (exchange) => {
            try {
                const response = await fetch(exchange.url);
                const data = await response.json();
                return { name: exchange.name, data: data };
            } catch (error) {
                console.error(`Error fetching data from ${exchange.name}:`, error);
                return { name: exchange.name, data: null };
            }
        })
    );

    return results;
};

// Function to update exchange data in the dashboard
const updateExchangeData = async () => {
    const loading = document.getElementById("loading");
    loading.style.display = "flex"; // Show loading spinner

    const exchangeData = await fetchExchangeData();
    loading.style.display = "none"; // Hide loading spinner

    const exchangeList = document.getElementById("exchange-list");
    exchangeList.innerHTML = ""; // Clear existing exchanges

    exchangeData.forEach(exchange => {
        const exchangeCard = document.createElement("div");
        exchangeCard.className = "exchange-card";
        exchangeCard.innerHTML = `
            <h3>${exchange.name}</h3>
            <p>${exchange.data ? JSON.stringify(exchange.data) : 'Data not available'}</p>
        `;
        exchangeList.appendChild(exchangeCard);
    });
};

// Call updateExchangeData every 5 seconds
setInterval(updateExchangeData, 5000);

// Initial call to set up the exchange data
updateExchangeData();