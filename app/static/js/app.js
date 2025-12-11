/**
 * Paprika Storyboard Generator - Main Application Entry
 * 
 * This is the main initialization file that wires together all modules.
 * Individual functionality is split into focused modules:
 * - state.js: Application state management
 * - ui.js: UI utilities (loading, errors, toasts)
 * - modal.js: Image preview modal
 * - frame-edit.js: Frame editing functionality
 * - storyboard.js: Storyboard generation and rendering
 */

/**
 * Initialize application on DOM ready
 */
document.addEventListener('DOMContentLoaded', initApp);

/**
 * Main application initialization
 */
function initApp() {
    // Initialize all modules
    window.UI.init();
    window.Modal.init();
    window.FrameEdit.init();
    window.Storyboard.init();
    
    // Global keyboard handlers
    document.addEventListener('keydown', handleGlobalKeydown);
    
    // Focus input on load
    document.getElementById('textInput').focus();
    
    console.log('Paprika Storyboard Generator initialized');
}

/**
 * Global keyboard event handler
 */
function handleGlobalKeydown(e) {
    if (e.key === 'Escape') {
        window.Modal.close();
        window.FrameEdit.closeModal();
    }
}

/**
 * Utility: Promise-based delay
 */
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Export utility
window.delay = delay;
