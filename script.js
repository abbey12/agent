const messageBox = document.querySelector('.message-box');
const inputField = document.querySelector('.messagebar input');
const sendButton = document.querySelector('.messagebar button');

sendButton.addEventListener('click', sendMessage);
inputField.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const messageText = inputField.value.trim();
    if (messageText) {
        const userMessage = document.createElement('div');
        userMessage.classList.add('chat', 'message');
        userMessage.textContent = messageText;
        messageBox.appendChild(userMessage);
        inputField.value = '';

        // Simulate a response
        setTimeout(() => {
            const responseMessage = document.createElement('div');
            responseMessage.classList.add('chat', 'response');
            responseMessage.textContent = "This is a simulated response.";
            messageBox.appendChild(responseMessage);
            messageBox.scrollTop = messageBox.scrollHeight; // Scroll to the bottom
        }, 1000);
        
        messageBox.scrollTop = messageBox.scrollHeight; // Scroll to the bottom
    }
}
