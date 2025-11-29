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
let userMessageDiv = document.createElement('div');

let isLoading = false;

// Scroll input-area above mobile keyboard on focus
inputBox.addEventListener('focus', function() {
    // On mobile, ensure input is visible above keyboard
    setTimeout(() => {
        // Multiple scroll approaches for mobile compatibility
        try {
            // Approach 1: scrollIntoView with different options
            this.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest',
                inline: 'nearest'
            });
            
            // Approach 2: Manual viewport adjustment
            const rect = this.getBoundingClientRect();
            const viewportHeight = window.innerHeight;
            const keyboardHeight = viewportHeight * 0.4; // Estimate keyboard height
            
            if (rect.bottom > viewportHeight - keyboardHeight) {
                const scrollAmount = rect.bottom - (viewportHeight - keyboardHeight) + 20;
                window.scrollBy(0, scrollAmount);
            }
        } catch (e) {
            console.log('Focus scroll failed:', e);
        }
    }, 300);
});

// Scroll back to show header when keyboard disappears
inputBox.addEventListener('blur', function() {
    // When keyboard disappears, scroll back to top to show header
    setTimeout(() => {
        try {
            // Multiple approaches to scroll back to top
            document.documentElement.scrollTop = 0;
            document.body.scrollTop = 0;
            window.scrollTo({ top: 0, left: 0, behavior: 'smooth' });
            
            // Also scroll the chat container to latest messages
            const chatContainer = document.getElementById('chat-container');
            if (chatContainer) {
                chatContainer.scrollTo({
                    top: chatContainer.scrollHeight,
                    behavior: 'smooth'
                });
                setTimeout(() => {
                    if(userMessageDiv)
                        chatContainer.scrollTo({
                            top: userMessageDiv.offsetTop-70,
                            behavior: 'smooth'
                        });
                    }, 100);
            }
        } catch (e) {
            console.log('Blur scroll failed:', e);
        }
    }, 300);
});

// Scroll indicator
const scrollIndicator = document.createElement('div');
scrollIndicator.className = 'scroll-indicator';
scrollIndicator.style.opacity = '0.5';
scrollIndicator.innerHTML = `
    <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
    </svg>
`;
// Append to main-container or body instead of chatContainer
const mainContainer = document.querySelector('.content') ;
mainContainer.appendChild(scrollIndicator);
scrollIndicator.addEventListener('click', () => {
    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
    });
});

function updateScrollIndicator() {
    const isNearBottom = chatContainer.scrollHeight - chatContainer.scrollTop - chatContainer.clientHeight < 100;
    if (isNearBottom) {
        scrollIndicator.classList.remove('visible');
    } else {
        scrollIndicator.classList.add('visible');
    }
}

// Listen for scroll events on chatContainer
chatContainer.addEventListener('scroll', updateScrollIndicator);
// Also call once on load to set initial state
updateScrollIndicator();

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

// Force full screen at loading
function forceFullScreen() {
    // Multiple approaches for mobile scroll
    try {
        // Method 1: Force scroll with different approaches
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
        window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
        
        // Method 2: Force via CSS
        document.body.style.overflow = 'hidden';
        setTimeout(() => {
            document.body.style.overflow = '';
        }, 100);
        
        // Method 3: Hide address bar on mobile by adding temporary content
        if (window.innerHeight < window.outerHeight) {
            const tempDiv = document.createElement('div');
            tempDiv.style.height = '200vh';
            tempDiv.style.position = 'absolute';
            tempDiv.style.top = '0';
            tempDiv.style.left = '0';
            tempDiv.style.width = '1px';
            tempDiv.style.zIndex = '-1';
            document.body.appendChild(tempDiv);
            
            setTimeout(() => {
                window.scrollTo(0, 1);
                setTimeout(() => {
                    window.scrollTo(0, 0);
                    // Safe removal check
                    if (tempDiv && tempDiv.parentNode) {
                        tempDiv.parentNode.removeChild(tempDiv);
                    }
                }, 50);
            }, 50);
        }
    } catch (e) {
        console.log('Scroll failed:', e);
    }
    
    // Try to request fullscreen if supported
    if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen().catch(() => {
            // Fullscreen failed, that's OK
        });
    } else if (document.documentElement.webkitRequestFullscreen) {
        document.documentElement.webkitRequestFullscreen().catch(() => {
            // Fullscreen failed, that's OK
        });
    }
}

// Force fullscreen on page load
window.addEventListener('load', forceFullScreen);

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

// Placeholder handler for legal link
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
        // Blur the input to trigger keyboard dismissal and scroll back
        this.blur();
    }
});

// Send button click
sendButton.addEventListener('click', () => {
    console.log("Send button clicked");
    sendMessage();
    // Blur the input to trigger keyboard dismissal and scroll back
    inputBox.blur();
});

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
    
    // Get the previous assistant message (if exists) before adding new user message
    const messages = chatContainer.querySelectorAll('.message.assistant');
    
    // Add user message
    userMessageDiv = addMessage(question, 'user');
    
    // Create assistant message container with loading spinner and padding to push question to top
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    // Add padding-bottom to create space that keeps question at top
    const containerHeight = chatContainer.clientHeight;
    messageDiv.style.paddingBottom = `${containerHeight - 50}px`;
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
            <div class="message-actions" style="display:none">
                <button class="action-btn copy-btn" title="Copier" style="border-radius:50%;padding:8px;background:#f3f3f3;border:none;box-shadow:0 1px 4px rgba(0,0,0,0.07);margin-right:6px;cursor:pointer;">
                    <i class="bi bi-clipboard" style="font-size:1.3em;"></i>
                </button>
                <button class="action-btn share-btn" title="Partager" style="border-radius:50%;padding:8px;background:#f3f3f3;border:none;box-shadow:0 1px 4px rgba(0,0,0,0.07);cursor:pointer;">
                    <i class="bi bi-share" style="font-size:1.3em;"></i>
                </button>
            </div>
        </div>
    `;
    chatContainer.appendChild(messageDiv);
    const contentDiv = messageDiv.querySelector('.message-text');
    const actionsDiv = messageDiv.querySelector('.message-actions');
    const copyBtn = messageDiv.querySelector('.copy-btn');
    const shareBtn = messageDiv.querySelector('.share-btn');
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(contentDiv.textContent);
    });

    shareBtn.addEventListener('click', () => {
        if (navigator.share) {
            navigator.share({
                text: contentDiv.textContent
            });
        } else {
            alert('Le partage n\'est pas supporté sur ce navigateur.');
        }
    });
    
    // Calculate scroll position to show the question without overlapping
    // setTimeout(() => {
    //     // Scroll to show the user message at the top
    //     chatContainer.scrollTo({
    //         top: userMessageDiv.offsetTop,
    //         behavior: 'smooth'
    //     });
    // }, 100);
    
    // Clear input
    inputBox.value = '';
    inputBox.style.height = 'auto';
    
    // Disable input
    isLoading = true;
    sendButton.disabled = true;
    inputBox.disabled = true;
    
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
            if (done) {
                // Fin du streaming : afficher les contrôles
                actionsDiv.style.display = '';
                break;
            }
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
                            // Keep padding - it will be filled by growing content
                        }
                        contentDiv.textContent += data.chunk;
                        updateScrollIndicator();
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
        messageDiv.style.paddingBottom = `50px`;
        // Re-enable input
        isLoading = false;
        sendButton.disabled = false;
        inputBox.disabled = false;
        updateScrollIndicator();
    }
}

function addMessage(text, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `
        <div class="message-icon">${role === 'user' ? 'U' : 'Ben'}</div>
        <div class="message-content">${escapeHtml(text)}</div>
    `;
    chatContainer.appendChild(messageDiv);
    // Don't auto-scroll here, let sendMessage handle it
    return messageDiv;
}



function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
