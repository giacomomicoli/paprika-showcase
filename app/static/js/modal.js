/**
 * Paprika Storyboard Generator - Modal Module
 * Handles image preview modal functionality
 */

/**
 * Modal DOM elements - populated by initModal()
 */
const modalElements = {
    overlay: null,
    image: null
};

/**
 * Initialize modal element references
 */
function initModal() {
    modalElements.overlay = document.getElementById('modalOverlay');
    modalElements.image = document.getElementById('modalImage');
    
    // Event listeners
    modalElements.overlay.addEventListener('click', handleModalClose);
}

/**
 * Open image preview modal
 */
function openModal(imageSrc) {
    modalElements.image.src = imageSrc;
    modalElements.overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

/**
 * Close image preview modal
 */
function closeModal() {
    modalElements.overlay.classList.remove('active');
    document.body.style.overflow = '';
}

/**
 * Handle modal overlay click (close on background click)
 */
function handleModalClose(e) {
    if (e.target === modalElements.overlay) {
        closeModal();
    }
}

// Export for use by other modules and global access
window.Modal = {
    init: initModal,
    open: openModal,
    close: closeModal
};

// Global function access for onclick handlers
window.openModal = openModal;
window.closeModal = closeModal;
