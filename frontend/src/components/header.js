// Create a reusable header component
class Header extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        this.innerHTML = `
            <header>
                <nav>
                    <div class="logo">
                        <a href="/">🔮 Mystic Tarot NFT</a>
                    </div>
                    <div class="wallet-status">
                        <w3m-button></w3m-button>
                        <w3m-network-button></w3m-network-button>
                    </div>
                </nav>
            </header>
        `;
    }
}

customElements.define('app-header', Header);
