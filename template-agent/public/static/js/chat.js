// ===================================
// CHAT MESSAGING FUNCTIONALITY
// ===================================

/**
 * Chat module
 * Handles message sending, streaming responses, and message UI
 */

// Global state
let isLoading = false;
let sessionId = null;
let userMessageDiv = document.createElement('div');
let currentAbortController = null;
let currentReader = null;

// Rate limiting - Debouncing
let lastRequestTime = 0;
const MIN_REQUEST_INTERVAL = 2000; // 2 seconds minimum between requests

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Add message to chat
 */
function addMessage(text, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `
        <div class="message-icon">${role === 'user' ? 'U' : 'IMX'}</div>
        <div class="message-content">${escapeHtml(text)}</div>
    `;
    
    const inputBox = document.getElementById('input-box');
    if (inputBox) {
        inputBox.value = '';
        inputBox.style.height = 'auto';
    }
    
    return messageDiv;
}

/**
 * Create assistant message with loading state
 */
function createAssistantMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    messageDiv.innerHTML = `
        <div class="message-icon">IMX</div>
        <div class="message-content">
            <div class="message-text">
                <div class="loading">
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                </div>
            </div>
            <div class="message-actions" style="display:none">
                <button class="action-btn copy-btn" title="" style="border-radius:50%;padding:8px;background:#f3f3f3;border:none;box-shadow:0 1px 4px rgba(0,0,0,0.07);margin-right:6px;cursor:pointer;width:40px;height:40px;display:inline-flex;align-items:center;justify-content:center;">
                    <i class="bi bi-clipboard" style="font-size:1.3em;"></i>
                </button>
                <button class="action-btn share-btn" title="" style="border-radius:50%;padding:8px;background:#f3f3f3;border:none;box-shadow:0 1px 4px rgba(0,0,0,0.07);margin-right:6px;cursor:pointer;width:40px;height:40px;display:inline-flex;align-items:center;justify-content:center;">
                    <i class="bi bi-share" style="font-size:1.3em;"></i>
                </button>
                <button class="action-btn like-btn" title="Like" style="border-radius:50%;padding:8px;background:#e6f9e6;border:none;box-shadow:0 1px 4px rgba(0,0,0,0.07);margin-left:6px;cursor:pointer;width:40px;height:40px;display:inline-flex;align-items:center;justify-content:center;">
                    <i class="bi bi-hand-thumbs-up" style="font-size:1.3em;"></i>
                </button>
                <button class="action-btn dislike-btn" title="Dislike" style="border-radius:50%;padding:8px;background:#f9e6e6;border:none;box-shadow:0 1px 4px rgba(0,0,0,0.07);margin-left:2px;cursor:pointer;width:40px;height:40px;display:inline-flex;align-items:center;justify-content:center;">
                    <i class="bi bi-hand-thumbs-down" style="font-size:1.3em;"></i>
                </button>
                <button class="action-btn tts-btn" title="" style="border-radius:50%;padding:8px;background:#c1ddf1;border:none;box-shadow:0 1px 4px rgba(0,0,0,0.07);margin-left:2px;cursor:pointer;width:40px;height:40px;display:inline-flex;align-items:center;justify-content:center;">
                    <i class="bi bi-volume-up" style="font-size:1.3em;"></i>
                </button>
            </div>
        </div>
    `;
    return messageDiv;
}

/**
 * Setup message action buttons
 */
function setupMessageActions(messageDiv, contentDiv) {
    const { t, BACKEND_URL } = window.ConfigModule;
    const { speakText, stopTTS, getActiveTtsButton } = window.TTSModule || {};
    
    const copyBtn = messageDiv.querySelector('.copy-btn');
    const shareBtn = messageDiv.querySelector('.share-btn');
    const likeBtn = messageDiv.querySelector('.like-btn');
    const dislikeBtn = messageDiv.querySelector('.dislike-btn');
    const ttsBtn = messageDiv.querySelector('.tts-btn');

    // Set translated titles
    if (ttsBtn) ttsBtn.title = t('messages.listen') || 'Listen';
    if (copyBtn) copyBtn.title = t('messages.copy');
    if (shareBtn) shareBtn.title = t('messages.share');

    // TTS button
    if (ttsBtn && speakText && stopTTS && getActiveTtsButton) {
        ttsBtn.addEventListener('click', () => {
            if (getActiveTtsButton() === ttsBtn) {
                stopTTS();
                return;
            }
            
            let textToSpeak;
            const translationResult = contentDiv.querySelector('.translation-result > div:last-child');
            if (translationResult) {
                textToSpeak = translationResult.textContent || translationResult.innerText;
            } else {
                textToSpeak = contentDiv.textContent || contentDiv.innerText;
            }
            
            if (textToSpeak && textToSpeak.trim()) {
                speakText(textToSpeak, ttsBtn);
            }
        });
    }

    // Like/dislike buttons
    if (likeBtn) {
        likeBtn.addEventListener('click', async () => {
            const questionId = likeBtn.dataset.questionId;
            if (!questionId) {
                console.log('Like button clicked but no question_id available');
                return;
            }
            likeBtn.style.background = '#49fc49ff';
            if (dislikeBtn) dislikeBtn.style.background = '#f9e6e6';
            
            fetch(`${BACKEND_URL}/api/like_answer`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question_id: questionId, like: true })
            }).then(res => res.json())
              .then(result => {
                  if (result.status !== 'success') {
                      console.log('Like vote failed:', result.message);
                  }
              })
              .catch(e => console.log('Like vote error:', e));
        });
    }
    
    if (dislikeBtn) {
        dislikeBtn.addEventListener('click', () => {
            const questionId = dislikeBtn.dataset.questionId;
            if (!questionId) {
                console.log('Dislike button clicked but no question_id available');
                return;
            }
            dislikeBtn.style.background = '#ff8686';
            if (likeBtn) likeBtn.style.background = '#e6f9e6';
            
            fetch(`${BACKEND_URL}/api/like_answer`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question_id: questionId, like: false })
            }).then(res => res.json())
              .then(result => {
                  if (result.status !== 'success') {
                      console.log('Dislike vote failed:', result.message);
                  }
              })
              .catch(e => console.log('Dislike vote error:', e));
        });
    }

    // Copy button
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(contentDiv.textContent);
        });
    }

    // Share button
    if (shareBtn) {
        shareBtn.addEventListener('click', () => {
            if (navigator.share) {
                navigator.share({ text: contentDiv.textContent });
            } else {
                alert(t('messages.shareNotSupported'));
            }
        });
    }
}

/**
 * Remove previous bottom spacer
 */
function removePreviousSpacer() {
    const previousSpacer = document.getElementById('chat-bottom-spacer');
    if (previousSpacer && previousSpacer.parentNode) {
        previousSpacer.remove();
    }
}

/**
 * Create bottom spacer
 */
function createBottomSpacer(userMsgDiv, assistantMsgDiv, offset = 10) {
    const bottomSpacer = document.createElement('div');
    bottomSpacer.id = 'chat-bottom-spacer';
    bottomSpacer.style.height = offset + 'px';
    bottomSpacer.style.flexShrink = '0';
    return bottomSpacer;
}

/**
 * Scroll to message bottom
 */
function scrollToMessageBottom(assistantMsgDiv, offset = 0) {
    const chatContainer = document.getElementById('chat-container');
    if (!chatContainer) return;
    
    const targetTop = assistantMsgDiv.offsetTop + assistantMsgDiv.offsetHeight - chatContainer.clientHeight + offset;
    if (targetTop > 0) {
        chatContainer.scrollTop = targetTop;
    }
}

/**
 * Prepare UI for loading
 */
function prepareUIForLoading() {
    isLoading = true;
    const sendButton = document.getElementById('send-button');
    const stopButton = document.getElementById('stop-button');
    const inputBox = document.getElementById('input-box');
    const voiceButton = document.getElementById('voice-button');
    
    // Toggle send/stop buttons
    if (sendButton) sendButton.style.display = 'none';
    if (stopButton) stopButton.style.display = '';
    if (inputBox) inputBox.disabled = true;
    if (voiceButton) voiceButton.disabled = true;
}

/**
 * Cancel ongoing message
 */
function cancelMessage() {
    if (currentAbortController) {
        currentAbortController.abort();
        currentAbortController = null;
    }
    if (currentReader) {
        currentReader.cancel().catch(() => {});
        currentReader = null;
    }
}

/**
 * Cleanup after message
 */
function cleanupAfterMessage(messageDiv) {
    isLoading = false;
    currentAbortController = null;
    currentReader = null;
    const sendButton = document.getElementById('send-button');
    const stopButton = document.getElementById('stop-button');
    const inputBox = document.getElementById('input-box');
    const voiceButton = document.getElementById('voice-button');
    
    // Toggle stop/send buttons
    if (stopButton) stopButton.style.display = 'none';
    if (sendButton) sendButton.style.display = '';
    if (inputBox) inputBox.disabled = false;
    if (voiceButton) voiceButton.disabled = false;
    
    const { updateScrollIndicator } = window.UIUtilsModule || {};
    if (updateScrollIndicator) updateScrollIndicator();
}

/**
 * Display links/PMIDs
 */
function displayLinks(container, links) {
    if (!links || links.length === 0) return;
    
    const refsDiv = document.createElement('div');
    refsDiv.className = 'link-refs';
    refsDiv.innerHTML = `<strong>Références :</strong> ` +
        links.map(link => {
            const url = `https://google.com/search?q=${link}`;
            return `<a href="${url}" target="_blank" rel="noopener">${link}</a>`;
        }).join(', ');
    container.appendChild(refsDiv);
}

/**
 * Handle streaming response
 */
async function handleStreamingResponse(question, contentDiv, actionsDiv) {
    const { BACKEND_URL, getCurrentLanguage } = window.ConfigModule;
    const { updateScrollIndicator } = window.UIUtilsModule || {};
    const { getCurrentAgent } = window.AgentsModule || {};
    
    const requestData = {
        question: question,
        agent: 'agent',
        language: getCurrentLanguage(),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
        locale: navigator.language || (getCurrentLanguage() === 'en' ? 'en-US' : 'fr-FR'),
        session_id: sessionId
    };

    // Create abort controller for cancellation
    currentAbortController = new AbortController();

    const response = await fetch(`${BACKEND_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData),
        signal: currentAbortController.signal
    });

    if (!response.ok) {
        if (response.status === 429) {
            const lang = getCurrentLanguage();
            const rateLimitMsg = lang === 'fr' 
                ? 'Limite de requêtes atteinte. Vous avez dépassé le nombre maximum de questions autorisées (10 par heure). Veuillez réessayer plus tard.'
                : 'Rate limit reached. You have exceeded the maximum number of allowed questions (10 per hour). Please try again later.';
            throw new Error(rateLimitMsg);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    currentReader = reader;
    const decoder = new TextDecoder();
    let buffer = '';
    let questionId = null;
    let fullText = '';
    let linksReceived = null;

    while (true) {
        const { done, value } = await reader.read();

        if (done) {
            actionsDiv.style.display = '';
            if (questionId) {
                const likeBtn = actionsDiv.querySelector('.like-btn');
                const dislikeBtn = actionsDiv.querySelector('.dislike-btn');
                if (likeBtn) likeBtn.dataset.questionId = questionId;
                if (dislikeBtn) dislikeBtn.dataset.questionId = questionId;
            }
            if (typeof marked !== 'undefined') {
                contentDiv.innerHTML = marked.parse(fullText);
            } else {
                contentDiv.textContent = fullText;
            }
            if (linksReceived !== null) {
                displayLinks(contentDiv, linksReceived);
            }
            return { fullText };
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const message of lines) {
            if (!message.trim()) continue;

            const dataMatch = message.match(/^data: (.+)$/m);
            if (dataMatch) {
                const rawData = dataMatch[1];
                
                // Check for [DONE] marker
                if (rawData === '[DONE]') {
                    // Stream is complete, exit the loop
                    actionsDiv.style.display = '';
                    if (questionId) {
                        const likeBtn = actionsDiv.querySelector('.like-btn');
                        const dislikeBtn = actionsDiv.querySelector('.dislike-btn');
                        if (likeBtn) likeBtn.dataset.questionId = questionId;
                        if (dislikeBtn) dislikeBtn.dataset.questionId = questionId;
                    }
                    if (typeof marked !== 'undefined') {
                        contentDiv.innerHTML = marked.parse(fullText);
                    } else {
                        contentDiv.textContent = fullText;
                    }
                    if (linksReceived !== null) {
                        displayLinks(contentDiv, linksReceived);
                    }
                    return { fullText };
                }
                
                try {
                    const data = JSON.parse(rawData);

                    // Handle errors
                    if (data.error) {
                        console.error('Stream error:', data.error);
                        throw new Error(data.error);
                    }

                    if (data.session_id && !sessionId) {
                        sessionId = data.session_id;
                        window.sessionId = sessionId;
                        console.log('Session ID received:', sessionId);
                    }
                    
                    if (data.question_id && !questionId) {
                        questionId = data.question_id;
                        window.questionId = questionId;
                    }

                    if (data.links !== undefined) {
                        linksReceived = data.links;
                        console.log('Links received via stream:', linksReceived);
                    }

                    if (data.chunk) {
                        fullText += data.chunk;
                        if (typeof marked !== 'undefined') {
                            contentDiv.innerHTML = marked.parse(fullText);
                        } else {
                            contentDiv.textContent = fullText;
                        }
                        scrollToMessageBottom(contentDiv.closest('.message'));
                    }
                  
                    if (updateScrollIndicator) updateScrollIndicator();
                } catch (parseError) {
                    console.error('JSON parsing error:', parseError);
                    throw parseError;
                }
            }
        }
    }
}

/**
 * Main send message function
 */
async function sendMessage() {
    const inputBox = document.getElementById('input-box');
    const emptyState = document.getElementById('empty-state');
    const chatContainer = document.getElementById('chat-container');
    
    const question = inputBox ? inputBox.value.trim() : '';
    if (!question || isLoading) return;
    
    // Rate limiting - Check minimum interval between requests
    const now = Date.now();
    if (now - lastRequestTime < MIN_REQUEST_INTERVAL) {
        console.log('Please wait before sending another message');
        // Optional: Show a brief visual feedback
        if (inputBox) {
            inputBox.style.borderColor = '#ff9800';
            setTimeout(() => {
                inputBox.style.borderColor = '';
            }, 500);
        }
        return;
    }
    lastRequestTime = now;
    
    // Stop voice recording
    if (window.VoiceRecognitionModule && window.VoiceRecognitionModule.stopRecording) {
        window.VoiceRecognitionModule.stopRecording();
    }
    
    if (emptyState) {
        emptyState.style.display = 'none';
    }
    
    removePreviousSpacer();
    
    userMessageDiv = addMessage(question, 'user');
    const messageDiv = createAssistantMessage();
    
    if (chatContainer) {
        chatContainer.appendChild(userMessageDiv);
        chatContainer.appendChild(messageDiv);
    }
    
    const spacerDiv = createBottomSpacer(userMessageDiv, messageDiv);
    if (chatContainer) {
        chatContainer.appendChild(spacerDiv);
        
        // Set spacer height to push content up (viewport height - small offset)
        spacerDiv.style.height = (chatContainer.clientHeight - 100) + 'px';
        
        // Scroll to show user message at the top (with header offset)
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                chatContainer.scrollTop = userMessageDiv.offsetTop - 80;
            });
        });
    }

    const contentDiv = messageDiv.querySelector('.message-text');
    const actionsDiv = messageDiv.querySelector('.message-actions');
    
    setupMessageActions(messageDiv, contentDiv);
    prepareUIForLoading();
    scrollToMessageBottom(contentDiv.closest('.message'));

    try {
        await handleStreamingResponse(question, contentDiv, actionsDiv);
    } catch (error) {
        console.error('Message sending error:', error);
        const { t, getCurrentLanguage } = window.ConfigModule;
        
        // Check if it's a rate limit error
        if (error.message && (error.message.includes('Limite de requêtes') || error.message.includes('Rate limit'))) {
            contentDiv.innerHTML = `<div style="color: #d32f2f; padding: 10px; background: #ffebee; border-radius: 4px; border-left: 4px solid #d32f2f;">
                <strong>⚠️ ${error.message}</strong>
            </div>`;
        } else {
            contentDiv.textContent = t('messages.error');
        }
    } finally {
        cleanupAfterMessage(messageDiv);
        const { handleFocus } = window.UIUtilsModule || {};
        if (handleFocus) handleFocus();
        scrollToMessageBottom(contentDiv.closest('.message'));
    }
}

/**
 * Get loading state
 */
function isMessageLoading() {
    return isLoading;
}

// Export for use in other modules
window.ChatModule = {
    sendMessage,
    createAssistantMessage,
    setupMessageActions,
    addMessage,
    removePreviousSpacer,
    createBottomSpacer,
    scrollToMessageBottom,
    prepareUIForLoading,
    cancelMessage,
    cleanupAfterMessage,
    handleStreamingResponse,
    isMessageLoading
};
