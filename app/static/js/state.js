/**
 * Paprika Storyboard Generator - State Management
 * Centralized application state
 */

// Application state - single source of truth
const state = {
    isGenerating: false,
    isEditing: false,
    currentStep: 0,
    totalFrames: 0,
    currentFrame: 0,
    generatedData: null,
    eventSource: null,
    selectedFrameNumber: null,
    sessionId: null,
    storyboardContext: null
};

// Export for use by other modules
window.AppState = state;
