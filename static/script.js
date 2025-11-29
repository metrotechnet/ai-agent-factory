// ===================================
// DOM ELEMENTS & GLOBAL STATE
// ===================================

// Chat interface elements
const chatContainer = document.getElementById('chat-container');
const inputBox = document.getElementById('input-box');
const sendButton = document.getElementById('send-button');
const emptyState = document.getElementById('empty-state');

// Sidebar navigation elements
const menuToggle = document.getElementById('menu-toggle');
const sidebar = document.getElementById('sidebar');
const closeSidebar = document.getElementById('close-sidebar');
const overlay = document.getElementById('overlay');

// Cookie consent elements
const cookieBanner = document.getElementById('cookie-banner');
const cookieAccept = document.getElementById('cookie-accept');
const cookieDecline = document.getElementById('cookie-decline');

// Global state variables
let userMessageDiv = document.createElement('div'); // Reference to current user message
let isLoading = false; // Flag to prevent multiple simultaneous requests

// ===================================
// MOBILE INPUT HANDLING
// ===================================

/**
 * Handle input box focus on mobile devices
 * Ensures the input remains visible above the virtual keyboard
 */
inputBox.addEventListener('focus', function() {
    setTimeout(() => {
        try {
            // Primary approach: Use scrollIntoView for input visibility
            this.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest',
                inline: 'nearest'
            });
            
            // Fallback approach: Manual viewport adjustment for mobile keyboards
            const rect = this.getBoundingClientRect();
            const viewportHeight = window.innerHeight;
            const estimatedKeyboardHeight = viewportHeight * 0.4; // Approximate keyboard size
            
            // Check if input will be hidden by keyboard
            if (rect.bottom > viewportHeight - estimatedKeyboardHeight) {
                const scrollAmount = rect.bottom - (viewportHeight - estimatedKeyboardHeight) + 20;
                window.scrollBy(0, scrollAmount);
            }
        } catch (error) {
            console.log('Input focus scroll failed:', error);
        }
    }, 300); // Delay to allow keyboard animation
});

/**
 * Handle input box blur (when keyboard disappears)
 * Restores normal view and scrolls to show latest messages
 */
inputBox.addEventListener('blur', function() {
    setTimeout(() => {
        try {
            // Multiple approaches to ensure consistent scroll behavior across browsers
            document.documentElement.scrollTop = 0;
            document.body.scrollTop = 0;
            window.scrollTo({ top: 0, left: 0, behavior: 'smooth' });
            
            // Scroll chat container to show latest messages
            if (chatContainer) {
                chatContainer.scrollTo({
                    top: chatContainer.scrollHeight,
                    behavior: 'smooth'
                });
                
                // If there's a user message, scroll to show it with some offset
                if (userMessageDiv) {
                    chatContainer.scrollTo({
                        top: userMessageDiv.offsetTop - 70,
                        behavior: 'smooth'
                    });
                }
            }
        } catch (error) {
            console.log('Input blur scroll failed:', error);
        }
    }, 300); // Delay to allow keyboard dismissal
});

// ===================================
// SCROLL INDICATOR
// ===================================

/**
 * Create and manage scroll indicator for chat container
 * Shows when user needs to scroll down to see new messages
 */
const scrollIndicator = document.createElement('div');
scrollIndicator.className = 'scroll-indicator';
scrollIndicator.style.opacity = '0.5';
scrollIndicator.innerHTML = `
    <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
    </svg>
`;

// Attach scroll indicator to main content area
const mainContainer = document.querySelector('.content');
if (mainContainer) {
    mainContainer.appendChild(scrollIndicator);
}

// Handle scroll indicator click - scroll to bottom of chat
scrollIndicator.addEventListener('click', () => {
    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
    });
});

/**
 * Update scroll indicator visibility based on chat scroll position
 * Hides indicator when user is near the bottom of the chat
 */
function updateScrollIndicator() {
    const threshold = 100; // Pixels from bottom to consider "near bottom"
    const isNearBottom = chatContainer.scrollHeight - chatContainer.scrollTop - chatContainer.clientHeight < threshold;
    
    if (isNearBottom) {
        scrollIndicator.classList.remove('visible');
    } else {
        scrollIndicator.classList.add('visible');
    }
}

// Set up scroll indicator event listeners
chatContainer.addEventListener('scroll', updateScrollIndicator);
// Initialize indicator state on page load
updateScrollIndicator();

// ===================================
// COOKIE CONSENT MANAGEMENT
// ===================================

/**
 * Check if user has previously given cookie consent
 * Shows banner with delay if no consent found
 */
function checkCookieConsent() {
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) {
        // Show cookie banner after 1 second delay for better UX
        setTimeout(() => {
            cookieBanner.classList.add('show');
        }, 1000);
    }
}

// Handle cookie acceptance
cookieAccept.addEventListener('click', () => {
    localStorage.setItem('cookieConsent', 'accepted');
    cookieBanner.classList.remove('show');
});

// Handle cookie decline
cookieDecline.addEventListener('click', () => {
    localStorage.setItem('cookieConsent', 'declined');
    cookieBanner.classList.remove('show');
});

// Initialize cookie consent check on page load
checkCookieConsent();



// ===================================
// SIDEBAR NAVIGATION
// ===================================

/**
 * Open sidebar menu and show overlay
 */
menuToggle.addEventListener('click', () => {
    sidebar.classList.add('open');
    overlay.classList.add('active');
});

/**
 * Close sidebar menu using close button
 */
closeSidebar.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
});

/**
 * Close sidebar menu by clicking on overlay
 */
overlay.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
});

// ===================================
// LEGAL NOTICE POPUP
// ===================================

/**
 * Handle legal notice link click
 * Shows legal disclaimer popup and closes sidebar
 */
document.getElementById('legal-link').addEventListener('click', (e) => {
    e.preventDefault();
    showLegalNotice();
    // Close sidebar after opening legal notice
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
});

/**
 * Create and display legal notice popup with disclaimer text
 */
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
    
    // Set up close button handler
    const closeBtn = popup.querySelector('.legal-popup-close');
    closeBtn.addEventListener('click', () => {
        popup.remove();
    });
    
    // Close popup when clicking outside content area
    popup.addEventListener('click', (e) => {
        if (e.target === popup) {
            popup.remove();
        }
    });
}

// ===================================
// INPUT HANDLING & UI INTERACTIONS
// ===================================

/**
 * Auto-resize textarea based on content
 * Limits maximum height to prevent UI issues
 */
inputBox.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 200) + 'px';
});

/**
 * Handle keyboard input for sending messages
 * Enter = send message, Shift+Enter = new line
 */
inputBox.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
        // Dismiss mobile keyboard and trigger scroll restoration
        this.blur();
    }
});

/**
 * Handle send button click
 */
sendButton.addEventListener('click', () => {
    console.log("Send button clicked");
    sendMessage();
    // Dismiss mobile keyboard and trigger scroll restoration
    inputBox.blur();
});

/**
 * Handle suggestion card clicks
 * Fills input with suggestion text and sends message
 */
document.querySelectorAll('.suggestion-card').forEach(card => {
    card.addEventListener('click', function() {
        const suggestionText = this.querySelector('p').textContent;
        inputBox.value = suggestionText;
        sendMessage();
    });
});

// ===================================
// MESSAGE SENDING & STREAMING
// ===================================

/**
 * Main function to send user message and handle AI response
 * Manages UI state, streaming response, and error handling
 */
async function sendMessage() {
    const question = inputBox.value.trim();
    
    // Prevent sending empty messages or multiple simultaneous requests
    if (!question || isLoading) return;
    
    // Hide welcome/empty state when first message is sent
    if (emptyState) {
        emptyState.style.display = 'none';
    }
    
    // Create and add user message to chat
    userMessageDiv = addMessage(question, 'user');
    
    // Create assistant message container with loading state
    const messageDiv = createAssistantMessage();
    chatContainer.appendChild(messageDiv);
    
    // Get message components for manipulation
    const contentDiv = messageDiv.querySelector('.message-text');
    const actionsDiv = messageDiv.querySelector('.message-actions');
    
    // Set up message action buttons (copy/share)
    setupMessageActions(messageDiv, contentDiv);
    
    // Prepare UI for loading state
    prepareUIForLoading();
    
    try {
        // Send request to backend and handle streaming response
        await handleStreamingResponse(question, contentDiv, actionsDiv);
    } catch (error) {
        console.error('Message sending error:', error);
        contentDiv.textContent = 'Désolé, une erreur est survenue. Réessaie dans quelques instants.';
    } finally {
        // Clean up and restore UI state
        cleanupAfterMessage(messageDiv);
    }
}

/**
 * Create assistant message container with loading spinner
 * @returns {HTMLElement} The created message element
 */
function createAssistantMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    // Add padding to keep user question visible at top
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
    
    return messageDiv;
}

/**
 * Set up copy and share button functionality for a message
 * @param {HTMLElement} messageDiv - The message container
 * @param {HTMLElement} contentDiv - The message content element
 */
function setupMessageActions(messageDiv, contentDiv) {
    const copyBtn = messageDiv.querySelector('.copy-btn');
    const shareBtn = messageDiv.querySelector('.share-btn');
    
    // Copy message text to clipboard
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(contentDiv.textContent);
    });

    // Share message using Web Share API or fallback
    shareBtn.addEventListener('click', () => {
        if (navigator.share) {
            navigator.share({
                text: contentDiv.textContent
            });
        } else {
            alert('Le partage n\'est pas supporté sur ce navigateur.');
        }
    });
}

/**
 * Prepare UI for loading state during message sending
 */
function prepareUIForLoading() {
    // Clear and reset input
    inputBox.value = '';
    inputBox.style.height = 'auto';
    
    // Disable input controls during loading
    isLoading = true;
    sendButton.disabled = true;
    inputBox.disabled = true;
}

/**
 * Handle streaming response from the server
 * @param {string} question - The user's question
 * @param {HTMLElement} contentDiv - Element to display response content
 * @param {HTMLElement} actionsDiv - Element containing action buttons
 */
async function handleStreamingResponse(question, contentDiv, actionsDiv) {
    const response = await fetch(`/query?question=${encodeURIComponent(question)}`, {
        method: 'POST',
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    // Process streaming response chunks
    while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
            // Streaming complete - show action buttons
            actionsDiv.style.display = '';
            break;
        }
        
        // Decode and process new data
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // Keep incomplete message in buffer
        
        // Process each complete message line
        for (const message of lines) {
            if (!message.trim()) continue;
            
            const dataMatch = message.match(/^data: (.+)$/m);
            if (dataMatch) {
                try {
                    const data = JSON.parse(dataMatch[1]);
                    
                    // Remove loading spinner on first content chunk
                    const loadingDiv = contentDiv.querySelector('.loading');
                    if (loadingDiv) {
                        contentDiv.textContent = '';
                    }
                    
                    // Append new content chunk
                    contentDiv.textContent += data.chunk;
                    updateScrollIndicator();
                } catch (parseError) {
                    console.error('JSON parsing error:', parseError);
                }
            }
        }
    }
}

/**
 * Clean up UI state after message completion
 * @param {HTMLElement} messageDiv - The message container to clean up
 */
function cleanupAfterMessage(messageDiv) {
    // Restore normal padding
    messageDiv.style.paddingBottom = '50px';
    
    // Re-enable input controls
    isLoading = false;
    sendButton.disabled = false;
    inputBox.disabled = false;
    
    // Update scroll indicator
    updateScrollIndicator();
}

// ===================================
// UTILITY FUNCTIONS
// ===================================

/**
 * Add a new message to the chat container
 * @param {string} text - The message text content
 * @param {string} role - Message role ('user' or 'assistant')
 * @returns {HTMLElement} The created message element
 */
function addMessage(text, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `
        <div class="message-icon">${role === 'user' ? 'U' : 'Ben'}</div>
        <div class="message-content">${escapeHtml(text)}</div>
    `;
    chatContainer.appendChild(messageDiv);
    // Note: Scrolling is handled by the calling function for better control
    return messageDiv;
}

/**
 * Escape HTML characters to prevent XSS attacks
 * @param {string} text - Text to escape
 * @returns {string} HTML-escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
