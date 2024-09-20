document.addEventListener("DOMContentLoaded", () => {
    const errorList = document.getElementById('error-list');
    const clearErrorsButton = document.getElementById('clear-errors');

    // Function to display an error message
    function displayError(message) {
        const errorMessage = document.createElement('div');
        errorMessage.className = 'error';
        errorMessage.textContent = message;
        errorList.appendChild(errorMessage);
    }

    // Example error handling logic
    window.addEventListener('error', (event) => {
        displayError(`Error: ${event.message} at ${event.filename}:${event.lineno}`);
    });

    // Clear errors on button click
    clearErrorsButton.addEventListener('click', () => {
        errorList.innerHTML = ''; // Clear all error messages
    });

    // Example of triggering an error for demonstration
    setTimeout(() => {
        throw new Error("This is a simulated error for testing purposes.");
    }, 3000);
});