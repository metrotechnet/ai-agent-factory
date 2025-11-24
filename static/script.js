const chatContainer = document.getElementById('chat-container');
const inputBox = document.getElementById('input-box');
const sendButton = document.getElementById('send-button');
const emptyState = document.getElementById('empty-state');

let isLoading = false;

// Auto-resize textarea
inputBox.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 200) + 'px';
});

// Send message on Enter (Shift+Enter for new line)
inputBox.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send button click
sendButton.addEventListener('click', sendMessage);

// Suggestion cards click
document.querySelectorAll('.suggestion-card').forEach(card => {
    card.addEventListener('click', function() {
        inputBox.value = this.querySelector('p').textContent;
        sendMessage();
    });
});

async function sendMessage() {
    const question = inputBox.value.trim();
    
    if (!question || isLoading) return;
    
    // Hide empty state
    if (emptyState) {
        emptyState.style.display = 'none';
    }
    
    // Add user message
    addMessage(question, 'user');
    
    // Clear input
    inputBox.value = '';
    inputBox.style.height = 'auto';
    
    // Disable input
    isLoading = true;
    sendButton.disabled = true;
    inputBox.disabled = true;
    
    // Add loading message
    const loadingId = addLoadingMessage();
    
    try {
        // Send request to backend
        const response = await fetch(`/query?question=${encodeURIComponent(question)}`, {
            method: 'POST',
        });
        
        const data = await response.json();
        
        // Remove loading message
        removeMessage(loadingId);
        
        // Add assistant response
        addMessage(data.answer, 'assistant');
        
    } catch (error) {
        console.error('Error:', error);
        removeMessage(loadingId);
        addMessage('Sorry, there was an error processing your request. Please try again.', 'assistant');
    } finally {
        // Re-enable input
        isLoading = false;
        sendButton.disabled = false;
        inputBox.disabled = false;
        // Remove auto-focus to prevent keyboard from opening on mobile
        // inputBox.focus();
    }
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addMessage(text, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `
        <div class="message-icon">${role === 'user' ? 'U' : 'Ben'}</div>
        <div class="message-content">${escapeHtml(text)}</div>
    `;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return messageDiv;
}

function addLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = 'loading-message';
    messageDiv.innerHTML = `
        <div class="message-icon">Ben</div>
        <div class="message-content">
            <div class="loading">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        </div>
    `;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return 'loading-message';
}

function removeMessage(id) {
    const message = document.getElementById(id);
    if (message) {
        message.remove();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
