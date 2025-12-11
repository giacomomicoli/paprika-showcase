/**
 * Paprika Storyboard Generator - Storyboard Module
 * Handles storyboard generation, streaming, and frame rendering
 */

/**
 * Storyboard DOM elements - populated by initStoryboard()
 */
const storyboardElements = {
    textInput: null,
    charCount: null,
    generateBtn: null,
    framesGrid: null
};

/**
 * Initialize storyboard element references
 */
function initStoryboard() {
    storyboardElements.textInput = document.getElementById('textInput');
    storyboardElements.charCount = document.getElementById('charCount');
    storyboardElements.generateBtn = document.getElementById('generateBtn');
    storyboardElements.framesGrid = document.getElementById('framesGrid');
    
    // Event listeners
    storyboardElements.textInput.addEventListener('input', handleInputChange);
    storyboardElements.textInput.addEventListener('keydown', handleKeyDown);
    storyboardElements.generateBtn.addEventListener('click', handleGenerate);
}

/**
 * Handle input changes - update character count
 */
function handleInputChange() {
    const length = storyboardElements.textInput.value.length;
    storyboardElements.charCount.textContent = `${length} characters`;
    storyboardElements.generateBtn.disabled = length === 0;
}

/**
 * Handle keyboard shortcuts (Cmd/Ctrl + Enter)
 */
function handleKeyDown(e) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        const state = window.AppState;
        if (!state.isGenerating && storyboardElements.textInput.value.trim()) {
            handleGenerate();
        }
    }
}

/**
 * Handle generate button click - Uses SSE for real-time progress
 */
async function handleGenerate() {
    const state = window.AppState;
    const description = storyboardElements.textInput.value.trim();
    
    if (!description || state.isGenerating) return;

    state.isGenerating = true;
    state.currentStep = 0;
    state.totalFrames = 0;
    state.currentFrame = 0;

    // Update UI state
    window.UI.showLoading();
    window.UI.hideResults();
    window.UI.hideError();
    window.UI.resetProgress();

    try {
        const response = await fetch('/storyboard/generate-stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_description: description })
        });

        if (!response.ok) throw new Error('Failed to start generation');

        await processStreamResponse(response);
    } catch (error) {
        console.error('Generation error:', error);
        window.UI.showError(error.message);
        window.UI.showToast('Failed to generate storyboard', 'error');
        state.isGenerating = false;
        window.UI.hideLoading();
    }
}

/**
 * Process SSE stream response
 */
async function processStreamResponse(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const jsonStr = line.slice(6);
                if (jsonStr.trim()) {
                    try {
                        handleStreamEvent(JSON.parse(jsonStr));
                    } catch (e) {
                        console.error('Failed to parse SSE event:', e);
                    }
                }
            }
        }
    }
}

/**
 * Handle incoming SSE events
 */
function handleStreamEvent(event) {
    console.log('Stream event:', event);

    switch (event.type) {
        case 'step_start':
            handleStepStart(event);
            break;
        case 'step_progress':
            handleStepProgress(event);
            break;
        case 'step_complete':
            handleStepComplete(event);
            break;
        case 'complete':
            handleGenerationComplete(event);
            break;
        case 'error':
            handleGenerationError(event);
            break;
    }
}

/**
 * Handle step start event
 */
function handleStepStart(event) {
    const state = window.AppState;
    state.currentStep = event.step;
    
    if (event.total_frames) {
        state.totalFrames = event.total_frames;
    }
    
    const stepElement = document.querySelector(`.progress-step[data-step="${event.step}"]`);
    if (stepElement) {
        stepElement.classList.add('active');
        window.UI.updateStepText(stepElement, event.message);
    }
    
    window.UI.updateLoadingText(event.message);
}

/**
 * Handle step progress event (frame-by-frame)
 */
function handleStepProgress(event) {
    const state = window.AppState;
    state.currentFrame = event.current_frame;
    state.totalFrames = event.total_frames;
    
    const stepElement = document.querySelector(`.progress-step[data-step="${event.step}"]`);
    if (stepElement) {
        const progressPercent = (event.current_frame / event.total_frames) * 100;
        stepElement.style.setProperty('--progress', `${progressPercent}%`);
        stepElement.classList.add('in-progress');
        
        const progressText = event.generating 
            ? `Generating frame ${event.current_frame}/${event.total_frames}...`
            : `Generated frame ${event.current_frame}/${event.total_frames}`;
        window.UI.updateStepText(stepElement, progressText);
    }
    
    window.UI.updateLoadingText(event.message);
}

/**
 * Handle step complete event
 */
function handleStepComplete(event) {
    const stepElement = document.querySelector(`.progress-step[data-step="${event.step}"]`);
    if (stepElement) {
        stepElement.classList.remove('active', 'in-progress');
        stepElement.classList.add('completed');
        stepElement.style.setProperty('--progress', '100%');
        window.UI.updateStepText(stepElement, event.message);
    }
}

/**
 * Handle generation complete event
 */
function handleGenerationComplete(event) {
    const state = window.AppState;
    state.isGenerating = false;
    state.generatedData = event;
    
    window.UI.hideLoading();
    showResults(event);
    window.UI.showToast('Storyboard generated successfully!', 'success');
}

/**
 * Handle generation error event
 */
function handleGenerationError(event) {
    const state = window.AppState;
    state.isGenerating = false;
    window.UI.hideLoading();
    window.UI.showError(event.message);
    window.UI.showToast('Failed to generate storyboard', 'error');
}

/**
 * Show results with frame data
 */
function showResults(data) {
    const state = window.AppState;
    
    // Store context for frame editing
    state.storyboardContext = storyboardElements.textInput.value.trim();
    
    window.UI.showResultsSection();
    
    document.getElementById('frameCount').textContent = 
        `${data.total_frames} frames generated`;

    renderFrames(data);
    updatePdfLink(data);
}

/**
 * Render frame cards
 */
function renderFrames(data) {
    const state = window.AppState;
    storyboardElements.framesGrid.innerHTML = '';

    // Extract session ID
    let sessionId = data.session_id;
    if (!sessionId && data.storyboard_path) {
        const pathMatch = data.storyboard_path.match(/([a-f0-9-]+)\/storyboard\.pdf$/i);
        if (pathMatch) sessionId = pathMatch[1];
    }

    if (!sessionId) {
        console.error('Could not determine session ID');
        return;
    }
    
    state.sessionId = sessionId;

    for (let i = 1; i <= data.total_frames; i++) {
        const frameCard = createFrameCard(i, sessionId);
        storyboardElements.framesGrid.appendChild(frameCard);
    }
}

/**
 * Create a frame card element
 */
function createFrameCard(frameNumber, sessionId) {
    const card = document.createElement('div');
    card.className = 'frame-card slide-up';
    card.style.animationDelay = `${(frameNumber - 1) * 0.1}s`;
    card.dataset.frameNumber = frameNumber;

    const paddedNumber = String(frameNumber).padStart(3, '0');
    const imagePath = `/output/${sessionId}/frame_${paddedNumber}.png`;

    card.innerHTML = `
        <div class="frame-image-container">
            <img src="${imagePath}" alt="Frame ${frameNumber}" class="frame-image" 
                 onclick="openModal('${imagePath}')"
                 onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 16 9%22><rect fill=%22%231e1e3f%22 width=%2216%22 height=%229%22/><text x=%228%22 y=%225%22 text-anchor=%22middle%22 fill=%22%236b6b80%22 font-size=%221%22>Image not found</text></svg>'">
            <span class="frame-number">Frame ${frameNumber}</span>
            <div class="frame-select-checkbox" onclick="toggleFrameSelection(event, ${frameNumber})"></div>
            <button class="frame-edit-btn" onclick="openEditModal(${frameNumber}, '${imagePath}')">
                ✏️ Edit
            </button>
        </div>
        <div class="frame-content">
            <p class="frame-description">Generated frame ${frameNumber}</p>
        </div>
    `;

    return card;
}

/**
 * Update PDF download link
 */
function updatePdfLink(data) {
    if (!data.storyboard_path) return;
    
    const pdfLink = document.getElementById('pdfDownloadLink');
    const pathMatch = data.storyboard_path.match(/([a-f0-9-]+\/storyboard\.pdf)$/i);
    
    if (pathMatch) {
        pdfLink.href = `/output/${pathMatch[1]}`;
    } else if (data.session_id) {
        pdfLink.href = `/output/${data.session_id}/storyboard.pdf`;
    }
}

/**
 * New generation - reset state and UI
 */
function newGeneration() {
    const state = window.AppState;
    
    state.generatedData = null;
    state.sessionId = null;
    state.storyboardContext = null;
    state.selectedFrameNumber = null;
    
    window.UI.elements.heroSection.classList.remove('minimized');
    window.UI.hideResults();
    window.UI.hideError();
    window.UI.resetProgress();
    
    storyboardElements.textInput.value = '';
    storyboardElements.textInput.focus();
    handleInputChange();
}

// Export for use by other modules
window.Storyboard = {
    init: initStoryboard,
    generate: handleGenerate,
    newGeneration
};

// Global function access
window.newGeneration = newGeneration;
