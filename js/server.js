const express = require('express');
const fs = require('fs');
const path = require('path');
const http = require('http');
const WebSocket = require('ws');
const chokidar = require('chokidar'); // For file watching
const dotenv = require('dotenv'); // For environment variables

dotenv.config(); // Load environment variables from .env file
const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const PORT = process.env.PORT || 3000;

// Middleware for serving static files
app.use(express.static('public'));

// Function to notify all connected clients
const notifyClients = (filename) => {
    const message = JSON.stringify({ event: 'fileChanged', filename });
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
        }
    });
};

// Initialize file watcher using chokidar
const watcher = chokidar.watch('public', { persistent: true });

// Watch for changes and notify clients
watcher.on('all', (event, path) => {
    console.log(`File ${event}: ${path}`);
    notifyClients(path);
});

// Route to serve the homepage
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

// Start the server
server.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

// WebSocket connection handling
wss.on('connection', (ws) => {
    console.log('New client connected');

    ws.on('message', (message) => {
        console.log(`Received message: ${message}`);
        // Implement logic based on received messages if needed
    });

    ws.on('close', () => {
        console.log('Client disconnected');
    });
});

// Graceful shutdown
const shutdown = (signal) => {
    console.log(`Received ${signal}. Shutting down gracefully...`);
    watcher.close(); // Close the file watcher
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
};

// Handle termination signals
process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));