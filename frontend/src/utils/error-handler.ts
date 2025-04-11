export enum ErrorType {
    API_ERROR = 'API_ERROR',
    WALLET_ERROR = 'WALLET_ERROR',
    NETWORK_ERROR = 'NETWORK_ERROR',
    VALIDATION_ERROR = 'VALIDATION_ERROR',
    CARD_GENERATION_ERROR = 'CARD_GENERATION_ERROR',
}

export interface ErrorDetails {
    type: ErrorType;
    message: string;
    retry?: boolean;
    data?: any;
}

class ErrorHandler {
    private static instance: ErrorHandler;
    private errorListeners: ((error: ErrorDetails) => void)[] = [];

    private constructor() {}

    static getInstance(): ErrorHandler {
        if (!ErrorHandler.instance) {
            ErrorHandler.instance = new ErrorHandler();
        }
        return ErrorHandler.instance;
    }

    public addListener(callback: (error: ErrorDetails) => void) {
        this.errorListeners.push(callback);
    }

    public removeListener(callback: (error: ErrorDetails) => void) {
        this.errorListeners = this.errorListeners.filter(listener => listener !== callback);
    }

    public handleError(error: any): ErrorDetails {
        let errorDetails: ErrorDetails;

        if (error.response) {
            // API Error
            errorDetails = this.handleApiError(error);
        } else if (error.message && error.message.includes('wallet')) {
            // Wallet Error
            errorDetails = this.handleWalletError(error);
        } else if (error instanceof TypeError && error.message === 'Failed to fetch') {
            // Network Error
            errorDetails = {
                type: ErrorType.NETWORK_ERROR,
                message: 'Unable to connect to the server. Please check your internet connection.',
                retry: true
            };
        } else {
            // Unknown Error
            errorDetails = {
                type: ErrorType.API_ERROR,
                message: 'An unexpected error occurred. Please try again.',
                retry: true
            };
        }

        // Notify all listeners
        this.errorListeners.forEach(listener => listener(errorDetails));
        return errorDetails;
    }

    private handleApiError(error: any): ErrorDetails {
        const status = error.response?.status;
        let message = 'An error occurred while processing your request.';
        let retry = true;

        switch (status) {
            case 400:
                message = 'Invalid request. Please check your input.';
                retry = false;
                break;
            case 401:
                message = 'Please connect your wallet to continue.';
                retry = false;
                break;
            case 403:
                message = 'You do not have permission to perform this action.';
                retry = false;
                break;
            case 429:
                message = 'Too many requests. Please wait a moment and try again.';
                retry = true;
                break;
            case 500:
                message = 'Server error. Please try again later.';
                retry = true;
                break;
            case 503:
                message = 'Card generation service is currently unavailable. Please try again later.';
                retry = true;
                break;
        }

        return {
            type: ErrorType.API_ERROR,
            message,
            retry,
            data: error.response?.data
        };
    }

    private handleWalletError(error: any): ErrorDetails {
        let message = 'An error occurred with the wallet connection.';
        let retry = true;

        if (error.message.includes('User rejected')) {
            message = 'Wallet connection was rejected. Please try again.';
            retry = true;
        } else if (error.message.includes('network')) {
            message = 'Please switch to the correct network.';
            retry = true;
        }

        return {
            type: ErrorType.WALLET_ERROR,
            message,
            retry,
            data: error
        };
    }
}

export const errorHandler = ErrorHandler.getInstance();

// Usage example:
// try {
//     await someOperation();
// } catch (error) {
//     const errorDetails = errorHandler.handleError(error);
//     if (errorDetails.retry) {
//         // Show retry button
//     }
// }
