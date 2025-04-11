class LoadingSpinner extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    static get observedAttributes() {
        return ['size', 'color', 'message', 'progress'];
    }

    connectedCallback() {
        this.render();
    }

    attributeChangedCallback() {
        this.render();
    }

    private render() {
        const size = this.getAttribute('size') || '40px';
        const color = this.getAttribute('color') || '#ffd700';
        const message = this.getAttribute('message');
        const progress = this.getAttribute('progress');

        if (this.shadowRoot) {
            this.shadowRoot.innerHTML = `
                <style>
                    :host {
                        display: inline-flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                    }

                    .spinner {
                        width: ${size};
                        height: ${size};
                        border: 4px solid rgba(255, 255, 255, 0.1);
                        border-left-color: ${color};
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                    }

                    .message {
                        margin-top: 10px;
                        color: var(--text-light, #e0e0e0);
                        font-size: 14px;
                        text-align: center;
                    }

                    .progress {
                        margin-top: 5px;
                        width: 200px;
                        height: 4px;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 2px;
                        overflow: hidden;
                    }

                    .progress-bar {
                        height: 100%;
                        background: ${color};
                        width: ${progress || 0}%;
                        transition: width 0.3s ease;
                    }

                    @keyframes spin {
                        to {
                            transform: rotate(360deg);
                        }
                    }
                </style>

                <div class="spinner"></div>
                ${message ? `<div class="message">${message}</div>` : ''}
                ${progress ? `
                    <div class="progress">
                        <div class="progress-bar"></div>
                    </div>
                ` : ''}
            `;
        }
    }
}

customElements.define('loading-spinner', LoadingSpinner);

// Usage example:
// <loading-spinner 
//     size="60px" 
//     color="#ffd700" 
//     message="Generating your cards..." 
//     progress="50">
// </loading-spinner>
