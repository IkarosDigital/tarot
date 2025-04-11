export enum ToastType {
    ERROR = 'error',
    SUCCESS = 'success',
    WARNING = 'warning',
    INFO = 'info'
}

interface ToastOptions {
    message: string;
    type: ToastType;
    duration?: number;
    action?: {
        text: string;
        onClick: () => void;
    };
}

class ToastManager {
    private static instance: ToastManager;
    private container: HTMLDivElement;

    private constructor() {
        this.createContainer();
    }

    static getInstance(): ToastManager {
        if (!ToastManager.instance) {
            ToastManager.instance = new ToastManager();
        }
        return ToastManager.instance;
    }

    private createContainer() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .toast-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
            }

            .toast {
                min-width: 300px;
                margin-bottom: 10px;
                padding: 15px;
                border-radius: 8px;
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
                animation: slideIn 0.3s ease-out;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }

            .toast-content {
                flex-grow: 1;
                margin-right: 10px;
            }

            .toast-action {
                padding: 5px 10px;
                border-radius: 4px;
                border: 1px solid white;
                background: transparent;
                color: white;
                cursor: pointer;
                font-size: 14px;
            }

            .toast-close {
                background: transparent;
                border: none;
                color: white;
                cursor: pointer;
                padding: 0 5px;
                font-size: 18px;
                margin-left: 10px;
            }

            .toast.error {
                background: #ff4d4f;
            }

            .toast.success {
                background: #52c41a;
            }

            .toast.warning {
                background: #faad14;
            }

            .toast.info {
                background: #1890ff;
            }

            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    show(options: ToastOptions) {
        const toast = document.createElement('div');
        toast.className = `toast ${options.type}`;

        const content = document.createElement('div');
        content.className = 'toast-content';
        content.textContent = options.message;
        toast.appendChild(content);

        if (options.action) {
            const actionButton = document.createElement('button');
            actionButton.className = 'toast-action';
            actionButton.textContent = options.action.text;
            actionButton.onclick = () => {
                options.action!.onClick();
                this.closeToast(toast);
            };
            toast.appendChild(actionButton);
        }

        const closeButton = document.createElement('button');
        closeButton.className = 'toast-close';
        closeButton.textContent = '×';
        closeButton.onclick = () => this.closeToast(toast);
        toast.appendChild(closeButton);

        this.container.appendChild(toast);

        // Auto close after duration
        if (options.duration !== 0) {
            setTimeout(() => {
                this.closeToast(toast);
            }, options.duration || 3000);
        }
    }

    private closeToast(toast: HTMLDivElement) {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            if (toast.parentNode === this.container) {
                this.container.removeChild(toast);
            }
        }, 300);
    }

    error(message: string, action?: ToastOptions['action']) {
        this.show({ message, type: ToastType.ERROR, action });
    }

    success(message: string, action?: ToastOptions['action']) {
        this.show({ message, type: ToastType.SUCCESS, action });
    }

    warning(message: string, action?: ToastOptions['action']) {
        this.show({ message, type: ToastType.WARNING, action });
    }

    info(message: string, action?: ToastOptions['action']) {
        this.show({ message, type: ToastType.INFO, action });
    }
}

export const toast = ToastManager.getInstance();

// Usage example:
// toast.error('Failed to connect wallet', {
//     action: {
//         text: 'Retry',
//         onClick: () => connectWallet()
//     }
// });
