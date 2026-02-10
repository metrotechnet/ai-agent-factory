// ===================================
// ENABLE/DISABLE INPUT-AREA BASED ON URL ARGUMENT
// ===================================

function setInputAreaEnabled(enabled) {
    const inputArea = document.querySelector('.input-area');
    if (!inputArea) return;
    const textarea = inputArea.querySelector('textarea');
    const sendBtn = inputArea.querySelector('#send-button');
    const voiceBtn = inputArea.querySelector('#voice-button');
    if (enabled) {
        inputArea.classList.remove('disabled');
        if (textarea) textarea.disabled = false;
        if (sendBtn) sendBtn.disabled = false;
        if (voiceBtn) voiceBtn.disabled = false;
    } else {
        inputArea.classList.add('disabled');
        if (textarea) textarea.disabled = true;
        if (sendBtn) sendBtn.disabled = true;
        if (voiceBtn) voiceBtn.disabled = true;
    }
}

function checkDemo4836Argument() {
    // const urlParams = new URLSearchParams(window.location.search);
    // const demoArg = urlParams.get('code');
    // setInputAreaEnabled(demoArg === 'demo4836');
    setInputAreaEnabled(true); // Always enable input area
}

document.addEventListener('DOMContentLoaded', function() {
    checkDemo4836Argument();
});
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
    
    // Update agent selector labels
    if (typeof updateAgentSelectorLabels === 'function') {
        updateAgentSelectorLabels();
    }
    
    // Refresh agent-specific placeholders
    if (typeof switchAgent === 'function' && typeof currentAgent !== 'undefined') {
        switchAgent(currentAgent);
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
    updateFooterFromConfig();
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

// TTS (Text-to-Speech) state
const ttsToggle = document.getElementById('tts-toggle');
const ttsIconOn = ttsToggle ? ttsToggle.querySelector('.tts-icon-on') : null;
const ttsIconOff = ttsToggle ? ttsToggle.querySelector('.tts-icon-off') : null;
let ttsEnabled = false;
let ttsAudio = null; // Current Audio object for playback

// Agent state
let currentAgent = 'dok2u'; // 'dok2u' or 'translator'
const agentSelector = document.getElementById('agent-selector');
const translateOptions = document.getElementById('translate-options');
const targetLanguageSelect = document.getElementById('target-language');

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
// LEGAL NOTICE & PRIVACY POPUP
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
 * Handle privacy policy link click
 * Shows privacy policy popup and closes sidebar
 */
document.getElementById('privacy-link').addEventListener('click', (e) => {
    e.preventDefault();
    showPrivacyPolicy();
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
});

/**
 * Handle about link click
 * Shows about popup and closes sidebar
 */
document.getElementById('about-link').addEventListener('click', (e) => {
    e.preventDefault();
    showAbout();
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
});


/**
 * Create and display legal notice popup with disclaimer text
 */
function showLegalNotice() {
    const langData = translations[currentLanguage] || translations['fr'];
    const legalContent = langData.legal;
    let html = `<h2 style='margin-top:0;text-align:center;'>${legalContent.title}</h2>`;
    html += legalContent.content.map(line => {
            return `<p>${line}</p>`;
    }).join('');

    Swal.fire({
        title: '',
        html: `<div style="text-align:left;">${html}</div>`,
        confirmButtonText: t('sidebar.closeButton') || 'Fermer',
        customClass: {
            popup: 'legal-popup-swal',
            title: 'legal-popup-title',
            content: 'legal-popup-content'
        },
        width: 700
    });
}

/**
 * Create and display privacy policy popup
 */
function showPrivacyPolicy() {
    const langData = translations[currentLanguage] || translations['fr'];
    const privacy = langData.privacy;
    let html = `<h2 style='margin-top:0;text-align:center;'>${privacy.title}</h2>`;
    if (privacy.lastUpdate) {
        html += `<p><em>${privacy.lastUpdate}</em></p>`;
    }
    html += privacy.content.map(line => {
         if (/^\d+\./.test(line)) {
            return `<h3>${line}</h3>`;
        } else if (line.trim() === '') {
            return '';
        } else {
            return `<p>${line}</p>`;
        }
    }).join('');
    // Regrouper les <li> dans des <ul> selon les sections
    html = html.replace(/(<h3>[^<]+<\/h3>)(<li>.*?<\/li>)+/gs, function(match) {
        const h3 = match.match(/<h3>[^<]+<\/h3>/)[0];
        const lis = match.match(/<li>.*?<\/li>/gs).join('');
        return h3 + '<ul >' + lis + '</ul>';
    });
    Swal.fire({
        title: '',
        html: `<div style="text-align:left;">${html}</div>`,
        confirmButtonText: t('sidebar.closeButton') || 'Fermer',
        customClass: {
            popup: 'legal-popup-swal',
            title: 'legal-popup-title',
            content: 'legal-popup-content'
        },
        width: 700
    });
}

function showAbout() {

        const langData = translations[currentLanguage] || translations['fr'];
        const about = langData.about || {};
        let html = `<h2 style='margin-top:0;text-align:center;'>${about.title}</h2>`;

        // Si about.content est un tableau, afficher chaque ligne comme une puce
        if (Array.isArray(about.content)) {
            html += '<ul style="text-align:left;">';
            about.content.forEach(line => {
                if (line.trim() !== '') {
                    html += `<li style="margin-bottom:8px;">${line}</li>`;
                }
            });
            html += '</ul>';
        } else if (typeof about.content === 'string') {
            // Si c'est une string, afficher tel quel
            html += `<div style="text-align:left;">${about.content}</div>`;
        }

        Swal.fire({
            title:  '',
            html: `<div style="text-align:left;">${html}</div>`,
            icon: 'info',
            confirmButtonText: about.closeButton || 'Fermer',
            customClass: {popup: 'swal2-dok2u-about'}
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
 * Update the bottom spacer height based on current message sizes
 * and scroll to keep the bottom of the assistant message visible
 * @param {HTMLElement} assistantMsgDiv - The assistant message element
 */
function scrollToMessageBottom(assistantMsgDiv) {
    // Update spacer to shrink as message grows
    const spacer = document.getElementById('chat-bottom-spacer');
    if (spacer && userMessageDiv) {
        const spacerHeight = chatContainer.clientHeight - userMessageDiv.offsetHeight - assistantMsgDiv.offsetHeight - 50;
        spacer.style.height = (spacerHeight > 0 ? spacerHeight : 0) + 'px';
    }
    // Scroll so the bottom of the assistant message is visible
    const targetTop = assistantMsgDiv.offsetTop + assistantMsgDiv.offsetHeight - chatContainer.clientHeight + 20;
    if (targetTop > 0) {
        chatContainer.scrollTop = targetTop;
    }
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
    // Route to translation if translator agent is active
    if (currentAgent === 'translator') {
        return sendTranslation();
    }
    
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

    // Scroll to show user message and loading indicator
    requestAnimationFrame(() => {
        chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
    });

    
    // Get message components for manipulation
    const contentDiv = messageDiv.querySelector('.message-text');
    const actionsDiv = messageDiv.querySelector('.message-actions');
    
    // Set up message action buttons (copy/share)
    setupMessageActions(messageDiv, contentDiv);
    
    // Prepare UI for loading state
    prepareUIForLoading();
    
    try {
        // Send request to backend and handle streaming response
        const result = await handleStreamingResponse(question, contentDiv, actionsDiv);
        // Read response aloud if TTS is enabled (fallback if not received via stream)
        if (!result.ttsReceivedViaStream) {
            speakText(contentDiv.textContent);
        }
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
        <div class="message-icon">Dok2u</div>
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
        session_id: sessionId,  // Include session_id to maintain conversation context
        tts: ttsEnabled  // Request inline TTS audio in the stream
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
    let ttsReceivedViaStream = false;
    let ttsPendingQuestionId = null;

    // Show spinner on TTS button while waiting for inline audio
    const ttsOriginalContent = ttsToggle ? ttsToggle.innerHTML : '';
    if (ttsEnabled && ttsToggle) {
        ttsToggle.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
        ttsToggle.disabled = true;
    }
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
            // Fetch PMIDs in background 
            fetchAndDisplayPmids(contentDiv);
            // If TTS is pending, poll for the audio (keep spinner)
            if (ttsPendingQuestionId) {
                pollForTtsAudio(ttsPendingQuestionId, sessionId, ttsOriginalContent);
                ttsReceivedViaStream = true; // prevent fallback speakText
            } else if (ttsToggle && ttsToggle.disabled) {
                // Restore TTS button if spinner is still showing and no TTS pending
                ttsToggle.innerHTML = ttsOriginalContent;
                ttsToggle.disabled = false;
            }
            return { fullText, ttsReceivedViaStream };
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
                        window.sessionId = sessionId; // Store globally for later use
                        console.log('Session ID received:', sessionId);
                    }
                    // Store question_id from first chunk
                    if (data.question_id && !questionId) {
                        questionId = data.question_id;
                        window.questionId = questionId; // Store globally for later use
                        // Find the comment, like, and dislike buttons and set data-question-id
                        if (!commentBtn && actionsDiv) commentBtn = actionsDiv.querySelector('.comment-btn');
                        if (!likeBtn && actionsDiv) likeBtn = actionsDiv.querySelector('.like-btn');
                        if (!dislikeBtn && actionsDiv) dislikeBtn = actionsDiv.querySelector('.dislike-btn');
                        if (commentBtn) commentBtn.dataset.questionId = questionId;
                        if (likeBtn) likeBtn.dataset.questionId = questionId;
                        if (dislikeBtn) dislikeBtn.dataset.questionId = questionId;
                    }

                    // Handle TTS pending notification from stream
                    if (data.tts_pending) {
                        ttsPendingQuestionId = data.tts_pending;
                        console.log('TTS: generation started on server for', ttsPendingQuestionId);
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
                        // Auto-scroll to keep assistant message bottom visible
                        scrollToMessageBottom(contentDiv.closest('.message'));
                    }
                  
                    updateScrollIndicator();
                } catch (parseError) {
                    console.error('JSON parsing error:', parseError);
                }
            }
        }
    }
}

// Appelle l’API pour obtenir les PMIDs pertinents à la question et les affiche sous la réponse
async function fetchAndDisplayPmids( container) {
    try {
        // Use sessionId and questionId if available for accurate retrieval
        const payload = { };
        if (window.sessionId && window.questionId) {
            payload.session_id = window.sessionId;
            payload.question_id = window.questionId;
        }
        const res = await fetch('/api/pmids', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.pmids && data.pmids.length > 0) {
            const refsDiv = document.createElement('div');
            refsDiv.className = 'pmid-refs';
            refsDiv.innerHTML = `<strong>Références PubMed :</strong> ` +
                data.pmids.map(pmid => {
                    // Extraire juste le numéro
                    const num = pmid.replace(/[^\d]/g, '');
                    const url = `https://google.com/search?q=${pmid}`;
                    return `<a href="${url}" target="_blank" rel="noopener">${pmid}</a>`;
                }).join(', ');
            container.appendChild(refsDiv);
        }
    } catch (e) {
        console.error('Erreur lors de la récupération des PMIDs', e);
    }
}

/**
 * Poll the server for TTS audio that is being generated in a background thread.
 * @param {string} questionId - The question ID to fetch TTS for
 * @param {string} sid - The session ID
 * @param {string} originalBtnContent - Original TTS button HTML to restore
 */
async function pollForTtsAudio(questionId, sid, originalBtnContent) {
    const maxAttempts = 30; // ~15 seconds max
    const interval = 500;  // 500ms between polls
    
    // Show spinner on TTS button
    if (ttsToggle) {
        ttsToggle.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
        ttsToggle.disabled = true;
    }

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        try {
            const res = await fetch('/api/tts_result', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sid, question_id: questionId })
            });

            if (res.status === 202) {
                // Still generating, wait and retry
                await new Promise(r => setTimeout(r, interval));
                continue;
            }

            if (res.ok) {
                const audioBlob = await res.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                stopTTS();
                ttsAudio = new Audio(audioUrl);

                // Restore button icon and start speaking animation
                if (ttsToggle) {
                    ttsToggle.innerHTML = originalBtnContent;
                    ttsToggle.disabled = false;
                    ttsToggle.classList.add('speaking');
                }

                ttsAudio.addEventListener('ended', () => {
                    if (ttsToggle) ttsToggle.classList.remove('speaking');
                    URL.revokeObjectURL(audioUrl);
                    ttsAudio = null;
                });
                ttsAudio.addEventListener('error', () => {
                    if (ttsToggle) ttsToggle.classList.remove('speaking');
                    URL.revokeObjectURL(audioUrl);
                    ttsAudio = null;
                });

                await ttsAudio.play();
                console.log('TTS: playing audio from background thread');
                return;
            }

            // Error status
            console.error('TTS poll error:', res.status);
            break;
        } catch (err) {
            console.error('TTS poll fetch error:', err);
            break;
        }
    }

    // Restore button on failure/timeout
    if (ttsToggle) {
        ttsToggle.innerHTML = originalBtnContent;
        ttsToggle.disabled = false;
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
        <div class="message-icon">${role === 'user' ? 'U' : 'Dok2u'}</div>
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
// AGENT SWITCHING
// ===================================

/**
 * Switch between agents (dok2u assistant vs translator)
 */
function switchAgent(agent, userInitiated) {
    currentAgent = agent;
    const isTranslator = agent === 'translator';
    
    // Toggle translation options bar
    if (translateOptions) {
        translateOptions.style.display = isTranslator ? 'flex' : 'none';
    }
    
    // Update placeholder
    if (isTranslator) {
        inputBox.placeholder = t('translator.placeholder') || 'Entrez le texte à traduire...';
    } else {
        inputBox.placeholder = t('input.placeholder') || 'Pose-moi une question...';
    }
    
    // Hide intro/empty state only when user explicitly picks an agent
    if (userInitiated && emptyState) {
        emptyState.style.display = 'none';
    }

    // Clear chat messages when switching agents
    if (userInitiated && chatContainer) {
        chatContainer.querySelectorAll('.message, #chat-bottom-spacer').forEach(el => el.remove());
        
        // Show agent welcome message
        const welcomeKey = isTranslator ? 'agents.translator_welcome' : 'agents.dok2u_welcome';
        const welcomeText = t(welcomeKey) || (isTranslator 
            ? 'Enter text or record a voice message, then choose the target language.'
            : 'Ask me your questions about nutrition and health.');
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'message assistant';
        welcomeDiv.innerHTML = `
            <div class="message-icon">Dok2u</div>
            <div class="message-content">
                <div class="message-text">${welcomeText}</div>
            </div>
        `;
        chatContainer.appendChild(welcomeDiv);
    }
    
    // Update disclaimer
    const disclaimerEl = document.querySelector('.input-disclaimer');
    if (disclaimerEl) {
        disclaimerEl.textContent = isTranslator 
            ? (t('translator.disclaimer') || '⚠️ Traduction automatique. Vérifiez toujours le résultat.')
            : (t('input.disclaimer') || '⚠️ Peut contenir des erreurs.');
    }

    // Focus input only on user action
    if (userInitiated && inputBox) {
        inputBox.focus();
    }
}

// Agent selector event listener
if (agentSelector) {
    agentSelector.addEventListener('change', function() {
        switchAgent(this.value, true);
    });
}

// Agent card click listeners (intro suggestion cards)
document.querySelectorAll('.agent-card[data-agent]').forEach(card => {
    card.addEventListener('click', function() {
        const agent = this.getAttribute('data-agent');
        if (agentSelector) {
            agentSelector.value = agent;
        }
        switchAgent(agent, true);
    });
});

/**
 * Update agent selector option texts with translations
 */
function updateAgentSelectorLabels() {
    if (!agentSelector) return;
    const options = agentSelector.querySelectorAll('option');
    options.forEach(opt => {
        const key = opt.getAttribute('data-i18n-option');
        if (key) {
            const label = t(key);
            if (label && label !== key) {
                opt.textContent = label;
            }
        }
    });
}

// ===================================
// TRANSLATION FUNCTIONS
// ===================================

/**
 * Send a translation request (text) with streaming response
 */
async function sendTranslation() {
    const text = inputBox.value.trim();
    if (!text || isLoading) return;
    
    // Stop voice recording if active
    stopRecording();
    
    // Hide welcome state
    if (emptyState) emptyState.style.display = 'none';
    
    removePreviousSpacer();
    
    // Add user message
    userMessageDiv = addMessage(text, 'user');
    chatContainer.appendChild(userMessageDiv);
    
    // Create assistant message with loading
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.innerHTML = `
        <div class="message-icon">🌐</div>
        <div class="message-content">
            <div class="message-text">
                <div class="loading">
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                </div>
            </div>
        </div>
    `;
    chatContainer.appendChild(messageDiv);
    
    const spacerDiv = createBottomSpacer(userMessageDiv, messageDiv);
    chatContainer.appendChild(spacerDiv);
    
    const contentDiv = messageDiv.querySelector('.message-text');
    
    prepareUIForLoading();
    
    const targetLang = targetLanguageSelect ? targetLanguageSelect.value : 'en';
    
    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                target_language: targetLang,
                source_language: 'auto'
            })
        });
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullText = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                // Final render
                const targetName = targetLanguageSelect ? targetLanguageSelect.options[targetLanguageSelect.selectedIndex].text : targetLang;
                contentDiv.innerHTML = `
                    <div class="translation-result">
                        <div class="translation-label">${t('translator.result') || 'Traduction'} (${targetName})</div>
                        <div>${fullText}</div>
                    </div>
                `;
                break;
            }
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop() || '';
            
            for (const message of lines) {
                if (!message.trim()) continue;
                const dataMatch = message.match(/^data: (.+)$/m);
                if (dataMatch) {
                    try {
                        const data = JSON.parse(dataMatch[1]);
                        if (data.chunk) {
                            const loadingDiv = contentDiv.querySelector('.loading');
                            if (loadingDiv) contentDiv.textContent = '';
                            fullText += data.chunk;
                            contentDiv.textContent = fullText;
                            // Auto-scroll to keep assistant message bottom visible
                            scrollToMessageBottom(contentDiv.closest('.message'));
                        }
                    } catch (e) {
                        console.error('Parse error:', e);
                    }
                }
            }
            updateScrollIndicator();
        }
    } catch (error) {
        console.error('Translation error:', error);
        contentDiv.textContent = t('messages.error');
    } finally {
        cleanupAfterMessage(messageDiv);
        // Read translation aloud if TTS is enabled
        speakText(contentDiv.textContent);
    }
}

// ===================================
// TEXT-TO-SPEECH (TTS)
// ===================================

/**
 * Toggle TTS on/off
 */
if (ttsToggle) {
    ttsToggle.addEventListener('click', () => {
        ttsEnabled = !ttsEnabled;
        ttsToggle.classList.toggle('active', ttsEnabled);
        if (ttsIconOn && ttsIconOff) {
            ttsIconOn.style.display = ttsEnabled ? '' : 'none';
            ttsIconOff.style.display = ttsEnabled ? 'none' : '';
        }
        // Stop any current playback when turning off
        if (!ttsEnabled) {
            stopTTS();
        }
    });
}

/**
 * Stop current TTS audio playback
 */
function stopTTS() {
    if (ttsAudio) {
        ttsAudio.pause();
        ttsAudio.currentTime = 0;
        ttsAudio = null;
    }
    if (ttsToggle) {
        ttsToggle.classList.remove('speaking');
    }
}

/**
 * Read text aloud using OpenAI TTS via backend API
 * @param {string} text - The text to read aloud
 */
async function speakText(text) {
    if (!ttsEnabled || !text || text.trim().length === 0) {
        console.log('TTS skipped: enabled=' + ttsEnabled + ', text length=' + (text ? text.trim().length : 0));
        return;
    }
    
    // Stop any previous playback
    stopTTS();
    
    // Strip markdown/HTML for cleaner speech
    const cleanText = text
        .replace(/<[^>]*>/g, '')        // Remove HTML tags
        .replace(/\*\*(.+?)\*\*/g, '$1') // Bold
        .replace(/\*(.+?)\*/g, '$1')     // Italic
        .replace(/#{1,6}\s/g, '')        // Headers
        .replace(/```[\s\S]*?```/g, '')  // Code blocks
        .replace(/`([^`]+)`/g, '$1')     // Inline code
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Links
        .replace(/PMID:\s*\d+/gi, '')    // PMID references
        .replace(/\[\d+\]/g, '')         // Numbered citations [1], [2]
        .replace(/Références?\s*PubMed\s*:.*$/gim, '') // "Références PubMed:" lines
        .replace(/References?\s*:.*$/gim, '')           // "References:" lines
        .replace(/Sources?\s*:.*$/gim, '')              // "Sources:" lines
        .replace(/\n{2,}/g, '. ')        // Multiple newlines to pause
        .replace(/\n/g, ' ')             // Newlines to space
        .replace(/\s{2,}/g, ' ')         // Collapse extra spaces
        .trim();
    
    if (!cleanText) return;
    
    console.log('TTS: speaking', cleanText.length, 'chars, language:', currentLanguage);
    
    // Save original button content and show spinner while fetching
    const originalContent = ttsToggle ? ttsToggle.innerHTML : '';
    if (ttsToggle) {
        ttsToggle.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
        ttsToggle.disabled = true;
    }

    try {
        const response = await fetch('/api/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: cleanText,
                language: currentLanguage
            })
        });
        
        if (!response.ok) {
            const errText = await response.text();
            throw new Error(`TTS error: ${response.status} - ${errText}`);
        }
        
        const audioBlob = await response.blob();
        console.log('TTS audio blob size:', audioBlob.size, 'type:', audioBlob.type);
        const audioUrl = URL.createObjectURL(audioBlob);
        ttsAudio = new Audio(audioUrl);

        // Restore icon and start pulse when playback begins
        if (ttsToggle) {
            ttsToggle.innerHTML = originalContent;
            ttsToggle.disabled = false;
            ttsToggle.classList.add('speaking');
        }
        
        ttsAudio.addEventListener('ended', () => {
            if (ttsToggle) ttsToggle.classList.remove('speaking');
            URL.revokeObjectURL(audioUrl);
            ttsAudio = null;
        });
        
        ttsAudio.addEventListener('error', () => {
            console.error('TTS audio playback error');
            if (ttsToggle) ttsToggle.classList.remove('speaking');
            URL.revokeObjectURL(audioUrl);
            ttsAudio = null;
        });
        
        await ttsAudio.play();
    } catch (error) {
        console.error('TTS error:', error);
        // Restore button on error
        if (ttsToggle) {
            ttsToggle.innerHTML = originalContent;
            ttsToggle.disabled = false;
        }
        stopTTS();
    }
}

// ===================================
// INITIALIZATION
// ===================================

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    // Load translations and set up internationalization
    loadTranslations().then(() => {
        updateAgentSelectorLabels();
    });
    
    // Check for cookie consent
    checkCookieConsent();
    
    // Initialize speech recognition
    initSpeechRecognition();
    
    // Add language switcher for testing (comment out in production)
    // addLanguageSwitcher();
});


