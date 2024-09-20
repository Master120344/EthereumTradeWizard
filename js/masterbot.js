const ethBot = require('./ethBot');
const solanaBot = require('./solanaBot');
const maticBot = require('./maticBot');
const atomBot = require('./atomBot');
const uniswapBot = require('./uniswapBot');
const gasFees = require('./gasFees');

// Array to hold all bot instances
const bots = [
    { name: 'Ethereum Bot', instance: ethBot },
    { name: 'Solana Bot', instance: solanaBot },
    { name: 'Matic Bot', instance: maticBot },
    { name: 'ATOM Bot', instance: atomBot },
    { name: 'Uniswap Bot', instance: uniswapBot }
];

// Logger function for improved debugging and monitoring
const logger = (message) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${message}`);
};

// Function to start all bots with enhanced error handling
const startBots = async () => {
    logger("Starting all trading bots...");
    for (const bot of bots) {
        try {
            await bot.instance.start();
            logger(`${bot.name} started successfully.`);
        } catch (error) {
            logger(`Error starting ${bot.name}: ${error.message}`);
        }
    }
};

// Function to stop all bots safely
const stopBots = async () => {
    logger("Stopping all trading bots...");
    for (const bot of bots) {
        try {
            await bot.instance.stop();
            logger(`${bot.name} stopped successfully.`);
        } catch (error) {
            logger(`Error stopping ${bot.name}: ${error.message}`);
        }
    }
};

// Function to check gas fees and notify bots
const updateGasFees = async () => {
    try {
        logger("Updating gas fees...");
        const currentGasFee = await gasFees.getGasFee();
        logger(`Current gas fee: $${currentGasFee}`);

        for (const bot of bots) {
            bot.instance.updateGasFee(currentGasFee);
        }
    } catch (error) {
        logger(`Error updating gas fees: ${error.message}`);
    }
};

// Function to run periodic tasks
const runPeriodicTasks = () => {
    setInterval(updateGasFees, 60000); // Update gas fees every 60 seconds
};

// Command interface for controlling bots
const commandInterface = () => {
    const readline = require('readline').createInterface({
        input: process.stdin,
        output: process.stdout
    });

    const handleCommand = (input) => {
        const command = input.trim().toLowerCase();
        switch (command) {
            case 'status':
                bots.forEach(bot => {
                    logger(`${bot.name} is running: ${bot.instance.isRunning()}`);
                });
                break;
            case 'stop':
                stopBots().then(() => {
                    readline.close();
                    process.exit(0);
                });
                break;
            case 'restart':
                stopBots().then(() => startBots());
                break;
            case 'info':
                bots.forEach(bot => {
                    logger(`${bot.name} info: ${JSON.stringify(bot.instance.getInfo())}`);
                });
                break;
            default:
                logger("Unknown command. Available commands: status, stop, restart, info");
        }
    };

    readline.on('line', handleCommand);
    logger("Enter command (type 'status', 'stop', 'restart', or 'info'):");
};

// Start everything
const startMasterBot = async () => {
    await startBots();
    runPeriodicTasks();
    commandInterface();
};

startMasterBot().catch(error => {
    logger(`Failed to start master bot: ${error.message}`);
    process.exit(1);
});