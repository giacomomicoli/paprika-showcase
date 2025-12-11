/**
 * Paprika Storyboard Generator - Frame Edit Module
 * Handles single frame editing functionality
 */

/**
 * Edit modal DOM elements - populated by initFrameEdit()
 */
const editElements = {
    overlay: null,
    previewImage: null,
    instructionsInput: null,
    formContainer: null,
    loadingContainer: null,
    applyBtn: null
};

/**
 * Initialize edit modal element references
 */
function initFrameEdit() {
    editElements.overlay = document.getElementById('editModalOverlay');
    editElements.previewImage = document.getElementById('editPreviewImage');
    editElements.instructionsInput = document.getElementById('editInstructionsInput');
    editElements.formContainer = document.getElementById('editFormContainer');
    editElements.loadingContainer = document.getElementById('editLoadingContainer');
    editElements.applyBtn = document.getElementById('applyEditBtn');
    
    // Event listeners
    editElements.overlay.addEventListener('click', handleEditModalClose);
}

/**
 * Toggle frame selection (single selection mode)
 */
function toggleFrameSelection(event, frameNumber) {
    event.stopPropagation();
    
    const checkbox = event.target;
    const card = checkbox.closest('.frame-card');
    const state = window.AppState;
    
    // Deselect previously selected frame
    if (state.selectedFrameNumber !== null && state.selectedFrameNumber !== frameNumber) {
        const previousCard = document.querySelector(
            `.frame-card[data-frame-number="${state.selectedFrameNumber}"]`
        );
        if (previousCard) {
            previousCard.classList.remove('selected');
            const previousCheckbox = previousCard.querySelector('.frame-select-checkbox');
            if (previousCheckbox) {
                previousCheckbox.classList.remove('checked');
            }
        }
    }
    
    // Toggle current selection
    if (state.selectedFrameNumber === frameNumber) {
        card.classList.remove('selected');
        checkbox.classList.remove('checked');
        state.selectedFrameNumber = null;
    } else {
        card.classList.add('selected');
        checkbox.classList.add('checked');
        state.selectedFrameNumber = frameNumber;
    }
}

/**
 * Open edit modal for a specific frame
 */
function openEditModal(frameNumber, imagePath) {
    const state = window.AppState;
    state.selectedFrameNumber = frameNumber;
    
    // Update modal content
    document.getElementById('editFrameNumber').textContent = frameNumber;
    editElements.previewImage.src = imagePath + '?t=' + Date.now();
    editElements.instructionsInput.value = '';
    
    // Show form, hide loading
    editElements.formContainer.style.display = 'flex';
    editElements.loadingContainer.classList.remove('active');
    editElements.applyBtn.disabled = false;
    
    // Update frame card selection state
    updateFrameSelectionUI(frameNumber);
    
    // Show modal
    editElements.overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Focus on input
    setTimeout(() => editElements.instructionsInput.focus(), 100);
}

/**
 * Update frame card selection UI
 */
function updateFrameSelectionUI(selectedFrameNumber) {
    const cards = document.querySelectorAll('.frame-card');
    cards.forEach(card => {
        const cardFrameNumber = parseInt(card.dataset.frameNumber);
        const checkbox = card.querySelector('.frame-select-checkbox');
        
        if (cardFrameNumber === selectedFrameNumber) {
            card.classList.add('selected');
            if (checkbox) checkbox.classList.add('checked');
        } else {
            card.classList.remove('selected');
            if (checkbox) checkbox.classList.remove('checked');
        }
    });
}

/**
 * Close edit modal
 */
function closeEditModal() {
    editElements.overlay.classList.remove('active');
    document.body.style.overflow = '';
    window.AppState.isEditing = false;
}

/**
 * Handle edit modal overlay click
 */
function handleEditModalClose(e) {
    if (e.target === editElements.overlay && !window.AppState.isEditing) {
        closeEditModal();
    }
}

/**
 * Apply frame edit via API
 */
async function applyFrameEdit() {
    const state = window.AppState;
    const instructions = editElements.instructionsInput.value.trim();
    
    if (!instructions) {
        window.UI.showToast('Please enter edit instructions', 'error');
        return;
    }
    
    if (!state.sessionId || !state.selectedFrameNumber) {
        window.UI.showToast('No frame selected', 'error');
        return;
    }
    
    state.isEditing = true;
    
    // Show loading state
    editElements.formContainer.style.display = 'none';
    editElements.loadingContainer.classList.add('active');
    editElements.applyBtn.disabled = true;
    
    try {
        const response = await fetch('/storyboard/edit-frame', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                frame_number: state.selectedFrameNumber,
                edit_instructions: instructions,
                storyboard_context: state.storyboardContext || ''
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.UI.showToast(`Frame ${state.selectedFrameNumber} edited successfully!`, 'success');
            refreshFrameImage(state.sessionId, state.selectedFrameNumber);
            refreshPdfLink(state.sessionId);
            closeEditModal();
        } else {
            window.UI.showToast(data.message || 'Edit failed', 'error');
            showEditForm();
        }
    } catch (error) {
        console.error('Edit error:', error);
        window.UI.showToast('Failed to edit frame', 'error');
        showEditForm();
    }
    
    state.isEditing = false;
}

/**
 * Refresh frame image after edit
 */
function refreshFrameImage(sessionId, frameNumber) {
    const paddedNumber = String(frameNumber).padStart(3, '0');
    const newImagePath = `/output/${sessionId}/frame_${paddedNumber}.png?t=${Date.now()}`;
    
    const frameCard = document.querySelector(`.frame-card[data-frame-number="${frameNumber}"]`);
    if (frameCard) {
        const img = frameCard.querySelector('.frame-image');
        if (img) img.src = newImagePath;
    }
}

/**
 * Refresh PDF link after edit
 */
function refreshPdfLink(sessionId) {
    const pdfLink = document.getElementById('pdfDownloadLink');
    pdfLink.href = `/output/${sessionId}/storyboard.pdf?t=${Date.now()}`;
}

/**
 * Show edit form (after error)
 */
function showEditForm() {
    editElements.formContainer.style.display = 'flex';
    editElements.loadingContainer.classList.remove('active');
    editElements.applyBtn.disabled = false;
}

// Export for use by other modules
window.FrameEdit = {
    init: initFrameEdit,
    toggle: toggleFrameSelection,
    openModal: openEditModal,
    closeModal: closeEditModal,
    apply: applyFrameEdit
};

// Global function access for onclick handlers
window.toggleFrameSelection = toggleFrameSelection;
window.openEditModal = openEditModal;
window.closeEditModal = closeEditModal;
window.applyFrameEdit = applyFrameEdit;
