// Backend URL Configuration
// This file sets window.BACKEND_URL for the main config module (static/js/config.js)
// For local development with production backend, set to production URL
// For local backend development, change to http://localhost:8080
if (window.location.hostname === 'localhost' && window.location.port === '3000') {
    // LOCAL FRONTEND + PRODUCTION BACKEND (for debugging)
    window.BACKEND_URL = 'https://imx-translator-4ykvm5teta-uk.a.run.app';
    console.log('[Backend URL] Local frontend connected to PRODUCTION backend:', window.BACKEND_URL);
} else {
    // For production or same-origin requests
    window.BACKEND_URL = window.BACKEND_URL || '';
}
