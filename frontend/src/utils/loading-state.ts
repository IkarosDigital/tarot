export enum LoadingState {
    IDLE = 'idle',
    LOADING = 'loading',
    SUCCESS = 'success',
    ERROR = 'error'
}

interface LoadingOptions {
    id: string;
    message?: string;
    progress?: number;
}

class LoadingManager {
    private static instance: LoadingManager;
    private loadingStates: Map<string, LoadingState> = new Map();
    private loadingMessages: Map<string, string> = new Map();
    private loadingProgress: Map<string, number> = new Map();
    private listeners: Map<string, Set<(state: LoadingState, message?: string, progress?: number) => void>> = new Map();

    private constructor() {}

    static getInstance(): LoadingManager {
        if (!LoadingManager.instance) {
            LoadingManager.instance = new LoadingManager();
        }
        return LoadingManager.instance;
    }

    startLoading(options: LoadingOptions) {
        this.loadingStates.set(options.id, LoadingState.LOADING);
        if (options.message) {
            this.loadingMessages.set(options.id, options.message);
        }
        if (typeof options.progress === 'number') {
            this.loadingProgress.set(options.id, options.progress);
        }
        this.notifyListeners(options.id);
    }

    updateProgress(id: string, progress: number, message?: string) {
        this.loadingProgress.set(id, progress);
        if (message) {
            this.loadingMessages.set(id, message);
        }
        this.notifyListeners(id);
    }

    finishLoading(id: string, success: boolean = true) {
        this.loadingStates.set(id, success ? LoadingState.SUCCESS : LoadingState.ERROR);
        this.notifyListeners(id);
        
        // Clean up after a delay
        setTimeout(() => {
            this.loadingStates.delete(id);
            this.loadingMessages.delete(id);
            this.loadingProgress.delete(id);
            this.notifyListeners(id);
        }, 2000);
    }

    getState(id: string): LoadingState {
        return this.loadingStates.get(id) || LoadingState.IDLE;
    }

    getMessage(id: string): string | undefined {
        return this.loadingMessages.get(id);
    }

    getProgress(id: string): number | undefined {
        return this.loadingProgress.get(id);
    }

    addListener(id: string, callback: (state: LoadingState, message?: string, progress?: number) => void) {
        if (!this.listeners.has(id)) {
            this.listeners.set(id, new Set());
        }
        this.listeners.get(id)!.add(callback);
    }

    removeListener(id: string, callback: (state: LoadingState, message?: string, progress?: number) => void) {
        this.listeners.get(id)?.delete(callback);
    }

    private notifyListeners(id: string) {
        const state = this.getState(id);
        const message = this.getMessage(id);
        const progress = this.getProgress(id);
        this.listeners.get(id)?.forEach(callback => callback(state, message, progress));
    }
}

export const loadingManager = LoadingManager.getInstance();

// Usage example:
// // Start loading
// loadingManager.startLoading({
//     id: 'card-generation',
//     message: 'Generating your cards...'
// });
//
// // Update progress
// loadingManager.updateProgress('card-generation', 50, 'Halfway there...');
//
// // Finish loading
// loadingManager.finishLoading('card-generation', true);
