/**
 * Paprika Storyboard Generator - UI Utilities
 * Handles loading states, errors, and toast notifications
 */

/**
 * DOM Elements cache - populated by initUI()
 */
const uiElements = {
    heroSection: null,
    inputContainer: null,
    loadingContainer: null,
    resultsSection: null,
    errorContainer: null,
    toastContainer: null,
    generateBtn: null
};

/**
 * Initialize UI element references
 */
function initUI() {
    uiElements.heroSection = document.getElementById('heroSection');
    uiElements.inputContainer = document.getElementById('inputContainer');
    uiElements.loadingContainer = document.getElementById('loadingContainer');
    uiElements.resultsSection = document.getElementById('resultsSection');
    uiElements.errorContainer = document.getElementById('errorContainer');
    uiElements.toastContainer = document.getElementById('toastContainer');
    uiElements.generateBtn = document.getElementById('generateBtn');
}

/**
 * Show loading state
 */
function showLoading() {
    uiElements.heroSection.classList.add('minimized');
    uiElements.inputContainer.style.display = 'none';
    uiElements.loadingContainer.classList.add('active');
    uiElements.generateBtn.disabled = true;
}

/**
 * Hide loading state
 */
function hideLoading() {
    uiElements.loadingContainer.classList.remove('active');
    uiElements.inputContainer.style.display = 'block';
    uiElements.generateBtn.disabled = false;
}

/**
 * Show error state
 */
function showError(message) {
    uiElements.errorContainer.classList.add('active');
    document.getElementById('errorMessage').textContent = message;
}

/**
 * Hide error state
 */
function hideError() {
    uiElements.errorContainer.classList.remove('active');
}

/**
 * Show results section
 */
function showResultsSection() {
    uiElements.resultsSection.classList.add('active');
    uiElements.heroSection.classList.add('minimized');
}

/**
 * Hide results section
 */
function hideResults() {
    uiElements.resultsSection.classList.remove('active');
}

/**
 * Update loading text
 */
function updateLoadingText(message) {
    const loadingText = document.querySelector('.loading-text');
    if (loadingText) {
        loadingText.textContent = message;
    }
}

/**
 * Update step text content
 */
function updateStepText(stepElement, text) {
    const textSpan = stepElement.querySelector('.step-text');
    if (textSpan) {
        textSpan.textContent = text;
    }
}

/**
 * Reset progress steps to initial state
 */
function resetProgress() {
    const steps = document.querySelectorAll('.progress-step');
    const defaultTexts = [
        'Analyzing your description',
        'Generating frame images',
        'Creating PDF storyboard'
    ];
    
    steps.forEach((step, index) => {
        step.classList.remove('active', 'completed', 'in-progress');
        step.style.setProperty('--progress', '0%');
        updateStepText(step, defaultTexts[index] || '');
    });
}

/**
 * Toast notifications
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
    toast.innerHTML = `
        <span>${icon}</span>
        <span>${message}</span>
    `;
    
    uiElements.toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Export for use by other modules
window.UI = {
    elements: uiElements,
    init: initUI,
    showLoading,
    hideLoading,
    showError,
    hideError,
    showResultsSection,
    hideResults,
    updateLoadingText,
    updateStepText,
    resetProgress,
    showToast
};
