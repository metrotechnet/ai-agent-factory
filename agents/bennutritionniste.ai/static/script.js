// ===================================
// INTERNATIONALIZATION SYSTEM
// ===================================

let translations = {};
let currentLanguage = 'fr';

/**
 * Get URL parameter by name
 */
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

/**
 * Load translations from JSON file
 */
async function loadTranslations() {
    try {
        const response = await fetch('/api/get_config');
        translations = await response.json();
        
        // Language detection priority: URL parameter > browser language > stored preference
        const urlLang = getUrlParameter('lang');
        const browserLang = navigator.language || navigator.userLanguage;
        const langCode = browserLang.startsWith('en') ? 'en' : 'fr';
        const storedLang = localStorage.getItem('preferredLanguage');
        
        // Validate URL language parameter
        if (urlLang && (urlLang === 'en' || urlLang === 'fr')) {
            currentLanguage = urlLang;
            // Update stored preference when URL parameter is used
            localStorage.setItem('preferredLanguage', urlLang);
        } else {
            // Favor browser language over stored preference when no URL argument
            currentLanguage = langCode || storedLang;
            // Ensure URL parameter is set even when using browser/stored preference
            const url = new URL(window.location);
            url.searchParams.set('lang', currentLanguage);
            window.history.replaceState({}, '', url);
        }
        
        // Apply translations
        applyTranslations(currentLanguage);
    } catch (error) {
        console.error('Failed to load translations:', error);
        currentLanguage = 'fr';
    }
}

/**
 * Apply translations to all elements with data-i18n attributes
 */
function applyTranslations(lang) {
    const langData = translations[lang] || translations['fr'];
    
    // Update text content
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = getNestedValue(langData, key);
        if (translation) {
            element.textContent = translation;
        }
    });
    
    // Update placeholder attributes
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        const translation = getNestedValue(langData, key);
        if (translation) {
            element.placeholder = translation;
        }
    });
    

    
    // Update title attributes
    document.querySelectorAll('[data-i18n-title]').forEach(element => {
        const key = element.getAttribute('data-i18n-title');
        const translation = getNestedValue(langData, key);
        if (translation) {
            element.title = translation;
        }
    });
    
    // Update alt attributes
    document.querySelectorAll('[data-i18n-alt]').forEach(element => {
        const key = element.getAttribute('data-i18n-alt');
        const translation = getNestedValue(langData, key);
        if (translation) {
            element.alt = translation;
        }
    });
    
    // Update src attributes
    document.querySelectorAll('[data-i18n-src]').forEach(element => {
        const key = element.getAttribute('data-i18n-src');
        const translation = getNestedValue(langData, key);
        if (translation) {
            element.src = translation;
        }
    });
    
    // Update document title
    const titleElement = document.querySelector('title[data-i18n]');
    if (titleElement) {
        const key = titleElement.getAttribute('data-i18n');
        const translation = getNestedValue(langData, key);
        if (translation) {
            document.title = translation;
        }
    }
}

/**
 * Get nested value from object using dot notation
 */
function getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => {
        return current && current[key] !== undefined ? current[key] : null;
    }, obj);
}

/**
 * Switch language
 */
function switchLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('preferredLanguage', lang);
    
    // Update URL parameter
    const url = new URL(window.location);
    url.searchParams.set('lang', lang);
    window.history.replaceState({}, '', url);
    
    applyTranslations(lang);
}

/**
 * Get translation for a key
 */
function t(key) {
    const langData = translations[currentLanguage] || translations['fr'];
    return getNestedValue(langData, key) || key;
}

/**
 * Get current language
 */
function getCurrentLanguage() {
    return currentLanguage;
}

// ===================================
// DOM ELEMENTS & GLOBAL STATE
// ===================================

// Chat interface elements
const chatContainer = document.getElementById('chat-container');
const inputBox = document.getElementById('input-box');
const sendButton = document.getElementById('send-button');
const voiceButton = document.getElementById('voice-button');
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
let sessionId = null; // Session ID for conversation context

// Voice recording state
let recognition = null;
let isRecording = false;

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
 * Scroll all relevant containers and elements to the top and show latest messages
 */
function scrollAllToTheTop() {
    // Multiple approaches to ensure consistent scroll behavior across browsers
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
    window.scrollTo({ top: 0, left: 0, behavior: 'smooth' });
    console.log('scrollAllToTheTop :');
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
}

/**
 * Handle input box blur (when keyboard disappears)
 * Restores normal view and scrolls to show latest messages
 */
inputBox.addEventListener('blur', function() {
    setTimeout(() => {
        try {
            scrollAllToTheTop();
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
    
    const langData = translations[currentLanguage] || translations['fr'];
    const legalContent = langData.legal;
    
    popup.innerHTML = `
        <div class="legal-popup-content">
            <button class="legal-popup-close">&times;</button>
            <h2>${legalContent.title}</h2>
            <div class="legal-text">
                ${legalContent.content.map(line => line ? `<p>${line}</p>` : '').join('')}
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
 * Remove previous bottom spacer if it exists
 */
function removePreviousSpacer() {
    const previousSpacer = document.getElementById('chat-bottom-spacer');
    if (previousSpacer && previousSpacer.parentNode) {
        previousSpacer.remove();
    }
}

/**
 * Create and add bottom spacer to chat container
 * @param {HTMLElement} userMsgDiv - The user message element
 * @param {HTMLElement} assistantMsgDiv - The assistant message element
 */
function createBottomSpacer(userMsgDiv, assistantMsgDiv) {
    const bottomSpacer = document.createElement('div');
    bottomSpacer.id = 'chat-bottom-spacer';
    const spacerHeight = chatContainer.clientHeight - userMsgDiv.offsetHeight - assistantMsgDiv.offsetHeight - 50;
    bottomSpacer.style.height = (spacerHeight > 0 ? spacerHeight : 0) + 'px';
    bottomSpacer.style.flexShrink = '0';
    //bottomSpacer.style.border = 'red 1px solid '; // For debugging
    return bottomSpacer
}

/**
 * Handle send button click
 */
sendButton.addEventListener('click', () => {


    // Check if keyboard is likely visible (input is focused)
    const isKeyboardVisible = document.activeElement === inputBox;

    sendMessage();

    // After sending, scroll the user message to the top of chat container
    setTimeout(() => {
        if (userMessageDiv && chatContainer) {
            chatContainer.scrollTo({
                top: userMessageDiv.offsetTop - chatContainer.offsetTop,
                behavior: 'smooth'
            });
        }
    }, 100);

    // Only blur if keyboard is visible
    if (isKeyboardVisible) {
        inputBox.blur();
    }
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



/**
 * Main function to send user message and handle AI response
 * Manages UI state, streaming response, and error handling
 */
async function sendMessage() {
    const question = inputBox.value.trim();
    
    // Prevent sending empty messages or multiple simultaneous requests
    if (!question || isLoading) return;
    
    // Stop voice recording if active
    stopRecording();
    
    // Hide welcome/empty state when first message is sent
    if (emptyState) {
        emptyState.style.display = 'none';
    }
    
    // Remove previous spacer if any
    removePreviousSpacer();
    
    // Create and add user message to chat
    userMessageDiv = addMessage(question, 'user');
    
    // Create assistant message container with loading state
    const messageDiv = createAssistantMessage();
    
    // Append messages to the end
    chatContainer.appendChild(userMessageDiv);
    chatContainer.appendChild(messageDiv);
    
    // Add bottom spacer to ensure content can scroll properly
    const spacerDiv = createBottomSpacer(userMessageDiv, messageDiv);
    chatContainer.appendChild(spacerDiv);

    
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
        contentDiv.textContent = t('messages.error');
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
    
    // Set initial minimal height to fit icon and small space (100px)
    // messageDiv.style.paddingBottom = '50px';

    
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
                <button class="action-btn copy-btn" title="" style="border-radius:50%;padding:8px;background:#f3f3f3;border:none;box-shadow:0 1px 4px rgba(0,0,0,0.07);margin-right:6px;cursor:pointer;">
                    <i class="bi bi-clipboard" style="font-size:1.3em;"></i>
                </button>
                <button class="action-btn share-btn" title="" style="border-radius:50%;padding:8px;background:#f3f3f3;border:none;box-shadow:0 1px 4px rgba(0,0,0,0.07);margin-right:6px;cursor:pointer;">
                    <i class="bi bi-share" style="font-size:1.3em;"></i>
                </button>
                <button class="action-btn like-btn" title="Like" style="border-radius:50%;padding:8px;background:#e6f9e6;border:none;box-shadow:0 1px 4px rgba(0,0,0,0.07);margin-left:6px;cursor:pointer;">
                    <i class="bi bi-hand-thumbs-up" style="font-size:1.3em;"></i>
                </button>
                <button class="action-btn dislike-btn" title="Dislike" style="border-radius:50%;padding:8px;background:#f9e6e6;border:none;box-shadow:0 1px 4px rgba(0,0,0,0.07);margin-left:2px;cursor:pointer;">
                    <i class="bi bi-hand-thumbs-down" style="font-size:1.3em;"></i>
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
    const commentBtn = messageDiv.querySelector('.comment-btn');
    const likeBtn = messageDiv.querySelector('.like-btn');
    const dislikeBtn = messageDiv.querySelector('.dislike-btn');
    // Like/dislike buttons
    if (likeBtn) {
        likeBtn.addEventListener('click', async () => {
            const questionId = likeBtn.dataset.questionId || (commentBtn && commentBtn.dataset.questionId);
            if (!questionId) {
                alert(t('messages.error'));
                return;
            }
            likeBtn.disabled = true;
            dislikeBtn && (dislikeBtn.disabled = true);
            try {
                const res = await fetch('/api/like_answer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question_id: questionId, like: true })
                });
                const result = await res.json();
                if (result.status === 'success') {
                    likeBtn.style.background = '#49fc49ff';
                } else {
                    alert(result.message || t('messages.error'));
                }
            } catch (e) {
                alert(t('messages.network_error'));
            }
        });
    }
    if (dislikeBtn) {
        dislikeBtn.addEventListener('click', async () => {
            const questionId = dislikeBtn.dataset.questionId || (commentBtn && commentBtn.dataset.questionId);
            if (!questionId) {
                alert(t('messages.error'));
                return;
            }
            dislikeBtn.disabled = true;
            likeBtn && (likeBtn.disabled = true);
            try {
                const res = await fetch('/api/like_answer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question_id: questionId, like: false })
                });
                const result = await res.json();
                if (result.status === 'success') {
                    dislikeBtn.style.background = '#f86868ff';
                } else {
                    alert(result.message || t('messages.error'));
                }
            } catch (e) {
                alert(t('messages.network_error'));
            }
        });
    }

    // Set translated titles
    copyBtn.title = t('messages.copy');
    shareBtn.title = t('messages.share');
    if (commentBtn) commentBtn.title = t('messages.comment');

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
            alert(t('messages.shareNotSupported'));
        }
    });


}

/**
 * Prepare UI for loading state during message sending
 */
function prepareUIForLoading() {
    // Disable input controls during loading
    isLoading = true;
    sendButton.disabled = true;
    inputBox.disabled = true;
    voiceButton.disabled = true;

}

/**
 * Handle streaming response from the server
 * @param {string} question - The user's question
 * @param {HTMLElement} contentDiv - Element to display response content
 * @param {HTMLElement} actionsDiv - Element containing action buttons
 */
async function handleStreamingResponse(question, contentDiv, actionsDiv) {
    // Prepare request payload with language information and session_id
    const requestData = {
        question: question,
        language: currentLanguage,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
        locale: navigator.language || (currentLanguage === 'en' ? 'en-US' : 'fr-FR'),
        session_id: sessionId  // Include session_id to maintain conversation context
    };

    const response = await fetch('/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let questionId = null;
    let commentBtn = null;
    let likeBtn = null;
    let dislikeBtn = null;

    // For markdown streaming, accumulate the full text and render as HTML
    let fullText = '';
    while (true) {
        const { done, value } = await reader.read();

        if (done) {
            // Streaming complete - show action buttons
            actionsDiv.style.display = '';
            // Set questionId on comment, like, and dislike buttons if available
            if (questionId) {
                if (!commentBtn && actionsDiv) commentBtn = actionsDiv.querySelector('.comment-btn');
                if (!likeBtn && actionsDiv) likeBtn = actionsDiv.querySelector('.like-btn');
                if (!dislikeBtn && actionsDiv) dislikeBtn = actionsDiv.querySelector('.dislike-btn');
                if (commentBtn) commentBtn.dataset.questionId = questionId;
                if (likeBtn) likeBtn.dataset.questionId = questionId;
                if (dislikeBtn) dislikeBtn.dataset.questionId = questionId;
            }
            // Final markdown render
            if (typeof marked !== 'undefined') {
                contentDiv.innerHTML = marked.parse(fullText);
            } else {
                contentDiv.textContent = fullText;
            }
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

                    // Store session_id from first chunk
                    if (data.session_id && !sessionId) {
                        sessionId = data.session_id;
                        console.log('Session ID received:', sessionId);
                    }
                    // Store question_id from first chunk
                    if (data.question_id && !questionId) {
                        questionId = data.question_id;
                        // Find the comment, like, and dislike buttons and set data-question-id
                        if (!commentBtn && actionsDiv) commentBtn = actionsDiv.querySelector('.comment-btn');
                        if (!likeBtn && actionsDiv) likeBtn = actionsDiv.querySelector('.like-btn');
                        if (!dislikeBtn && actionsDiv) dislikeBtn = actionsDiv.querySelector('.dislike-btn');
                        if (commentBtn) commentBtn.dataset.questionId = questionId;
                        if (likeBtn) likeBtn.dataset.questionId = questionId;
                        if (dislikeBtn) dislikeBtn.dataset.questionId = questionId;
                    }

                    // Append new content chunk
                    if (data.chunk) {
                        // Remove loading spinner on first content chunk
                        const loadingDiv = contentDiv.querySelector('.loading');
                        if (loadingDiv) {
                            contentDiv.textContent = '';
                        }
                        fullText += data.chunk;
                        // Live preview (optional): render markdown as HTML if marked is available
                        if (typeof marked !== 'undefined') {
                            contentDiv.innerHTML = marked.parse(fullText);
                        } else {
                            contentDiv.textContent = fullText;
                        }
                    }
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
    // messageDiv.style.paddingBottom = '50px';
    
    // Re-enable input controls
    isLoading = false;
    sendButton.disabled = false;
    inputBox.disabled = false;
    voiceButton.disabled = false;
    
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
    // Clear the text area
    inputBox.value = '';
    inputBox.style.height = 'auto';

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

// ===================================
// VOICE RECOGNITION
// ===================================

/**
 * Initialize speech recognition
 */
function initSpeechRecognition() {
    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        console.warn('Speech recognition not supported in this browser');
        voiceButton.style.display = 'none';
        return;
    }
    
    recognition = new SpeechRecognition();
    recognition.continuous = false; // Disable continuous mode to prevent duplications
    recognition.interimResults = true;
    recognition.lang = currentLanguage === 'en' ? 'en-US' : 'fr-FR';
    
    let finalTranscript = '';
    
    recognition.onstart = function() {
        isRecording = true;
        voiceButton.classList.add('recording');
        finalTranscript = '';
        console.log('Voice recording onstart');
    };
    
    recognition.onresult = function(event) {
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Update input box with transcription
        inputBox.value = finalTranscript + interimTranscript;
        inputBox.style.height = 'auto';
        inputBox.style.height = Math.min(inputBox.scrollHeight, 200) + 'px';
    };
    
    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        stopRecording();
    };
    
    recognition.onend = function() {
        if (isRecording) {
            // Restart recognition to continue capturing speech
            try {
                recognition.start();
            } catch (error) {
                console.log('Recognition restart error:', error);
            }
        }
    };
}

/**
 * Toggle voice recording
 */
function toggleRecording() {
    if (!recognition) {
        alert(currentLanguage === 'en' 
            ? 'Speech recognition is not supported in your browser.' 
            : 'La reconnaissance vocale n\'est pas supportée par votre navigateur.');
        return;
    }
    
    if (isRecording) {
        sendMessage(); // Send message when stopping recording
        stopRecording();
    } else {
        startRecording();
    }
}

/**
 * Start voice recording
 */
function startRecording() {
    try {
        recognition.lang = currentLanguage === 'en' ? 'en-US' : 'fr-FR';
        recognition.start();
        console.log('Voice recording started');
    } catch (error) {
        console.error('Failed to start recording:', error);
    }
}

/**
 * Stop voice recording and clear text area
 */
function stopRecording() {
    if (recognition && isRecording) {
        isRecording = false;
        voiceButton.classList.remove('recording');
        recognition.stop();
        console.log('Voice recording stopped');
        

    }
}

// Voice button click handler
voiceButton.addEventListener('click', toggleRecording);

// ===================================
// INITIALIZATION
// ===================================

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    // Load translations and set up internationalization
    loadTranslations();
    
    // Check for cookie consent
    checkCookieConsent();
    
    // Initialize speech recognition
    initSpeechRecognition();
    
    // Add language switcher for testing (comment out in production)
    // addLanguageSwitcher();
});


