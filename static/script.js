const chatContainer = document.getElementById('chat-container');
const inputBox = document.getElementById('input-box');
const sendButton = document.getElementById('send-button');
const emptyState = document.getElementById('empty-state');
const menuToggle = document.getElementById('menu-toggle');
const sidebar = document.getElementById('sidebar');
const closeSidebar = document.getElementById('close-sidebar');
const overlay = document.getElementById('overlay');
const cookieBanner = document.getElementById('cookie-banner');
const cookieAccept = document.getElementById('cookie-accept');
const cookieDecline = document.getElementById('cookie-decline');

let isLoading = false;

// Cookie consent management
function checkCookieConsent() {
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) {
        setTimeout(() => {
            cookieBanner.classList.add('show');
        }, 1000);
    }
}

cookieAccept.addEventListener('click', () => {
    localStorage.setItem('cookieConsent', 'accepted');
    cookieBanner.classList.remove('show');
});

cookieDecline.addEventListener('click', () => {
    localStorage.setItem('cookieConsent', 'declined');
    cookieBanner.classList.remove('show');
});

// Check consent on page load
checkCookieConsent();

// Sidebar toggle
menuToggle.addEventListener('click', () => {
    sidebar.classList.add('open');
    overlay.classList.add('active');
});

closeSidebar.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
});

overlay.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
});

// Placeholder handlers for appointment and legal links
document.getElementById('appointment-link').addEventListener('click', (e) => {
    e.preventDefault();
    alert('Fonctionnalité de prise de rendez-vous à venir !');
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
});

document.getElementById('legal-link').addEventListener('click', (e) => {
    e.preventDefault();
    showLegalNotice();
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
});

function showLegalNotice() {
    const popup = document.createElement('div');
    popup.className = 'legal-popup';
    popup.innerHTML = `
        <div class="legal-popup-content">
            <button class="legal-popup-close">&times;</button>
            <h2>Avertissements</h2>
            <div class="legal-text">
                <p>Les informations fournies par cet agent d'intelligence artificielle sont générées automatiquement à partir de contenus existants et peuvent comporter des erreurs, imprécisions ou omissions.</p>
                <p>Elles sont communiquées à titre informatif uniquement et ne constituent en aucun cas des conseils médicaux, nutritionnels ou professionnels personnalisés.</p>
                <p>L'utilisation des réponses fournies se fait sous votre seule responsabilité.</p>
                <p>L'éditeur de l'agent et son créateur ne pourront être tenus responsables de tout dommage, direct ou indirect, résultant de l'utilisation des informations produites.</p>
                <p>Pour toute décision liée à votre santé, votre nutrition, votre entraînement, vos blessures ou toute autre situation personnelle, veuillez consulter un professionnel qualifié.</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(popup);
    
    // Close popup handlers
    const closeBtn = popup.querySelector('.legal-popup-close');
    closeBtn.addEventListener('click', () => {
        popup.remove();
    });
    
    popup.addEventListener('click', (e) => {
        if (e.target === popup) {
            popup.remove();
        }
    });
}

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
    
    // Create assistant message container with loading spinner
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.innerHTML = `
        <div class="message-icon">Ben</div>
        <div class="message-content">
            <div class="message-text">
                <div class="loading">
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                </div>
            </div>
            <div class="message-disclaimer">Peut contenir des erreurs. Ne remplace pas un avis professionnel.</div>
        </div>
    `;
    chatContainer.appendChild(messageDiv);
    const contentDiv = messageDiv.querySelector('.message-text');
    
    try {
        // Send request to backend with streaming
        const response = await fetch(`/query?question=${encodeURIComponent(question)}`, {
            method: 'POST',
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            
            // Keep the last incomplete message in buffer
            buffer = lines.pop() || '';
            
            for (const message of lines) {
                if (!message.trim()) continue;
                
                const dataMatch = message.match(/^data: (.+)$/m);
                if (dataMatch) {
                    try {
                        const data = JSON.parse(dataMatch[1]);
                        // Remove loading spinner on first chunk
                        const loadingDiv = contentDiv.querySelector('.loading');
                        if (loadingDiv) {
                            contentDiv.textContent = '';
                        }
                        contentDiv.textContent += data.chunk;
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                    } catch (parseError) {
                        console.error('Erreur de parsing:', parseError);
                    }
                }
            }
        }
        
    } catch (error) {
        console.error('Erreur:', error);
        contentDiv.textContent = 'Désolé, une erreur est survenue. Réessaie dans quelques instants.';
    } finally {
        // Re-enable input
        isLoading = false;
        sendButton.disabled = false;
        inputBox.disabled = false;
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



function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
