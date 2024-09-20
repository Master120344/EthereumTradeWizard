const config = {
    // Exchange API configurations
    exchanges: [
        {
            name: 'Binance',
            url: 'https://api.binance.com',
            apiKey: process.env.BINANCE_API_KEY,
            secret: process.env.BINANCE_API_SECRET,
            endpoints: {
                ticker: '/api/v3/ticker/price',
                orderBook: '/api/v3/depth',
                trades: '/api/v3/trades'
            }
        },
        {
            name: 'Coinbase',
            url: 'https://api.coinbase.com',
            apiKey: process.env.COINBASE_API_KEY,
            secret: process.env.COINBASE_API_SECRET,
            endpoints: {
                ticker: '/v2/prices',
                orderBook: '/v2/prices/spot',
                trades: '/v2/accounts'
            }
        },
        {
            name: 'Kraken',
            url: 'https://api.kraken.com',
            apiKey: process.env.KRAKEN_API_KEY,
            secret: process.env.KRAKEN_API_SECRET,
            endpoints: {
                ticker: '/0/public/Ticker',
                orderBook: '/0/public/Depth',
                trades: '/0/public/Trades'
            }
        },
        // Add additional exchanges here...
    ],

    // Gas fees API
    gasFeesAPI: 'https://api.gasstation.network/v2',
    gasFeeEndpoints: {
        eth: '/eth',
        bsc: '/bsc'
    },

    // Trading parameters
    tradingParams: {
        slippage: 0.5, // Allowed slippage in percentage
        minTradeAmount: 10, // Minimum trade amount
        maxTradeAmount: 1000, // Maximum trade amount
        retryAttempts: 5, // Number of attempts to retry failed trades
        timeout: 30000 // Timeout for API requests in milliseconds
    },

    // Fee configurations
    feeConfig: {
        tradingFeePercentage: 0.1, // Trading fee percentage
        withdrawalFee: 0.0005 // Example withdrawal fee
    },

    // WebSocket configurations
    websocketConfig: {
        url: 'wss://api.example.com', // Example WebSocket URL
        reconnectInterval: 5000, // Interval for reconnect attempts in milliseconds
        pingInterval: 30000 // Interval for sending pings to maintain connection
    },

    // Logging settings
    logging: {
        level: 'info', // Log levels: 'error', 'warn', 'info', 'debug'
        logFilePath: './logs/trading.log' // Path to log file
    },

    // Notification settings
    notifications: {
        email: {
            enabled: true,
            smtpServer: process.env.SMTP_SERVER,
            user: process.env.SMTP_USER,
            password: process.env.SMTP_PASSWORD,
            to: 'user@example.com' // Notification recipient
        },
        push: {
            enabled: true,
            service: 'pushbullet', // or 'pusher'
            accessToken: process.env.PUSH_ACCESS_TOKEN
        }
    }
};

module.exports = config;