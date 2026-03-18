/*
====================================================
 backend-url.js – Backend URL Configuration
----------------------------------------------------
 Sets window.BACKEND_URL for the main config module (static/js/config.js).
 Auto-generated during Firebase deployment from BACKEND_URL in .env.
 For local development, detects localhost:3000 and points to backend on 8080.
====================================================
*/

if (window.location.hostname === 'localhost' && window.location.port === '3000') {
    window.BACKEND_URL = 'http://localhost:8080';
} else {
    // For production or same-origin requests
    window.BACKEND_URL = window.BACKEND_URL || '';
}
