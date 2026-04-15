document.addEventListener('DOMContentLoaded', () => {
    // Chatbot functionality
    const chatToggle = document.getElementById('chatToggle');
    const chatBox = document.getElementById('chatBox');
    const chatInput = document.getElementById('chatInput');
    const sendChat = document.getElementById('sendChat');
    const chatMessages = document.getElementById('chatMessages');

    if (chatToggle) {
        chatToggle.addEventListener('click', () => {
            const isVisible = chatBox.style.display === 'flex';
            chatBox.style.display = isVisible ? 'none' : 'flex';
        });

        const appendMessage = (text, sender) => {
            const msgObj = document.createElement('div');
            msgObj.className = `message ${sender}`;
            msgObj.textContent = text;
            chatMessages.appendChild(msgObj);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };

        const sendMessage = () => {
            const text = chatInput.value.trim();
            if (!text) return;
            
            appendMessage(text, 'user');
            chatInput.value = '';

            // Send to backend
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            })
            .then(res => res.json())
            .then(data => {
                appendMessage(data.response, 'bot');
            })
            .catch(err => {
                appendMessage("Sorry, I'm having trouble connecting to the server.", 'bot');
            });
        };

        sendChat.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }

    // Modal click outside to close
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('addChildModal');
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});
