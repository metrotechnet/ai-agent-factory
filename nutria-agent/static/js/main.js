// ===================================
// MAIN INITIALIZATION & EVENT HANDLERS
// ===================================

/**
 * Main module
 * Initializes the application and sets up event handlers
 */

/**
 * Warm up the backend to avoid cold start delay on first user query
 */
async function warmupBackend() {
    const overlay = document.getElementById('initial-loading-overlay');
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
        
        const response = await fetch(`${window.BACKEND_URL}/health`, {
            method: 'GET',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            console.warn('Backend health check returned non-OK status:', response.status);
        }
    } catch (error) {
        // If timeout or network error, continue anyway - don't block the app
        console.warn('Backend warmup failed (continuing anyway):', error.message);
    } finally {
        // Hide loading overlay after warmup attempt
        if (overlay) {
            overlay.classList.add('hidden');
            // Remove from DOM after fade out
            setTimeout(() => {
                if (overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
            }, 500);
        }
    }
}

/**
 * Initialize all modules and event handlers
 */
document.addEventListener('DOMContentLoaded', async function() {
    // Warm up backend before initializing UI
    await warmupBackend();
    // Get modules
    const { loadConfig, switchLanguage, getCurrentLanguage, getMainConfig, populateSuggestionCards } = window.ConfigModule;
    const { isMobileDevice, initKeyboardDetection, createScrollIndicator, updateScrollIndicator, 
            initSidebar, initCookieConsent, initLegalLinks } = window.UIUtilsModule;
    const { sendMessage } = window.ChatModule;
    const { initSpeechRecognition, toggleRecording, toggleRecognitionMethod, useWhisper } = window.VoiceRecognitionModule;
    const { switchAgent, updateAgentSelectorLabels, updateSourceLanguageDisplay } = window.AgentsModule;
    const { componentRegistry, setTranslationReversed, isTranslationReversed } = window.ComponentsModule;
    
    // DOM elements
    const inputBox = document.getElementById('input-box');
    const sendButton = document.getElementById('send-button');
    const voiceButton = document.getElementById('voice-button');
    const languageSelector = document.getElementById('language-selector');
    const targetLanguageSelect = document.getElementById('target-language');
    const translationDirectionBtn = document.getElementById('translation-direction-btn');
    const chatContainer = document.getElementById('chat-container');
    const emptyState = document.getElementById('empty-state');
    

    
    // Load  agent directly (single-agent setup)
    await loadConfig();
    
    // Display agent intro (creates library selector dynamically)
    const { displayAgentIntro } = window.AgentsModule;
    if (displayAgentIntro) displayAgentIntro();
    
    // Render initial components
    const mainConfig = getMainConfig();
    const langData = mainConfig[getCurrentLanguage()] || mainConfig['fr'];
    
    // Render agent components
    if (langData.components) {
        if (langData.components.languageSelector) {
            componentRegistry.languageSelector.render(langData.components.languageSelector);
        } else {
            componentRegistry.languageSelector.hide();
        }
        
        if (langData.components.inputArea) {
            componentRegistry.inputArea.render(langData.components.inputArea);
        } else if (langData.input) {
            componentRegistry.inputArea.render(langData.input);
        }
    } else {
        componentRegistry.languageSelector.hide();
        if (langData.input) {
            componentRegistry.inputArea.render(langData.input);
        }
    }
    
    populateSuggestionCards(getCurrentLanguage());
    updateSourceLanguageDisplay();
    
    // Show body after config loads
    document.body.style.display = '';
    
    // Initialize UI components
    initSidebar();
    initCookieConsent();
    initLegalLinks();
    initSpeechRecognition();
    
    // Create scroll indicator
    const scrollIndicator = createScrollIndicator();
    if (chatContainer && scrollIndicator) {
        chatContainer.addEventListener('scroll', updateScrollIndicator);
        updateScrollIndicator();
    }
    
    // Initialize mobile keyboard detection
    if (isMobileDevice()) {
        initKeyboardDetection();
    }
    
    // ===================================
    // INPUT BOX EVENT HANDLERS
    // ===================================
    
    if (inputBox) {
        // Auto-resize textarea
        inputBox.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
        
        // Handle Enter key
        inputBox.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
                this.blur();
            }
        });
        
        // Handle focus for mobile
        inputBox.addEventListener('focus', function() {
            setTimeout(() => {
                try {
                    this.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'nearest',
                        inline: 'nearest'
                    });
                    
                    const rect = this.getBoundingClientRect();
                    const viewportHeight = window.innerHeight;
                    const estimatedKeyboardHeight = viewportHeight * 0.4;
                    
                    if (rect.bottom > viewportHeight - estimatedKeyboardHeight) {
                        const scrollAmount = rect.bottom - (viewportHeight - estimatedKeyboardHeight) + 20;
                        window.scrollBy(0, scrollAmount);
                    }
                } catch (error) {
                    console.log('Input focus scroll failed:', error);
                }
            }, 300);
        });
    }
    
    // ===================================
    // BUTTON EVENT HANDLERS
    // ===================================
    
    if (sendButton) {
        sendButton.addEventListener('click', () => {
            const isKeyboardVisible = document.activeElement === inputBox;
            sendMessage();
            if (isKeyboardVisible && inputBox) {
                inputBox.blur();
            }
        });
    }
    
    if (voiceButton) {
        voiceButton.addEventListener('click', toggleRecording);
    }
    
    // ===================================
    // LANGUAGE SELECTOR
    // ===================================
    
    if (languageSelector) {
        languageSelector.addEventListener('change', function() {
            switchLanguage(this.value);
        });
    }
    
    // ===================================
    // AGENT SELECTOR - Removed (single-agent setup)
    // ===================================
    
    // ===================================
    // TRANSLATION DIRECTION BUTTON
    // ===================================
    
    if (translationDirectionBtn) {
        translationDirectionBtn.addEventListener('click', function() {
            // Toggle reversed state
            const newReversed = !isTranslationReversed();
            setTranslationReversed(newReversed);
            
            // Swap the language selections
            updateSourceLanguageDisplay();
            console.log(`Translation direction reversed`);
        });
    }
    
    // ===================================
    // SPEECH METHOD INDICATOR
    // ===================================
    
    const speechMethodIndicator = document.getElementById('speech-method-indicator');
    if (speechMethodIndicator) {
        function updateIndicator() {
            if (useWhisper()) {
                speechMethodIndicator.textContent = '🎤 Whisper';
                speechMethodIndicator.style.background = '#4CAF50';
            } else {
                speechMethodIndicator.textContent = '🎤 Web Speech';
                speechMethodIndicator.style.background = '#2196F3';
            }
        }
        
        speechMethodIndicator.addEventListener('click', () => {
            toggleRecognitionMethod();
            updateIndicator();
        });
        
        updateIndicator();
    }
    
    console.log('Application initialized successfully');
});
