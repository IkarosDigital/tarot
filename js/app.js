class App {
    constructor() {
        this.web3Client = new Web3Client();
        this.initializeElements();
        this.addEventListeners();
        this.setupWeb3Handlers();
    }

    initializeElements() {
        // Buttons
        this.connectWalletBtn = document.getElementById('connectWalletBtn');
        this.startJourneyBtn = document.getElementById('startJourneyBtn');
        this.viewCollectionBtn = document.getElementById('viewCollectionBtn');
        
        // Display elements
        this.walletAddress = document.getElementById('walletAddress');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.loadingMessage = document.getElementById('loadingMessage');
    }

    addEventListeners() {
        this.connectWalletBtn.addEventListener('click', () => this.connectWallet());
        this.startJourneyBtn.addEventListener('click', () => this.startJourney());
        this.viewCollectionBtn.addEventListener('click', () => this.viewCollection());
    }

    setupWeb3Handlers() {
        this.web3Client.handleAccountChange = (address) => {
            this.updateWalletDisplay(address);
            this.enableButtons();
        };

        this.web3Client.handleDisconnect = () => {
            this.updateWalletDisplay(null);
            this.disableButtons();
        };
    }

    async connectWallet() {
        try {
            this.showLoading('Connecting to wallet...');
            const address = await this.web3Client.init();
            this.updateWalletDisplay(address);
            this.enableButtons();
        } catch (error) {
            console.error('Failed to connect wallet:', error);
            alert(error.message);
        } finally {
            this.hideLoading();
        }
    }

    updateWalletDisplay(address) {
        if (address) {
            this.connectWalletBtn.style.display = 'none';
            this.walletAddress.style.display = 'inline';
            this.walletAddress.textContent = `${address.slice(0, 6)}...${address.slice(-4)}`;
        } else {
            this.connectWalletBtn.style.display = 'inline';
            this.walletAddress.style.display = 'none';
            this.walletAddress.textContent = '';
        }
    }

    enableButtons() {
        this.startJourneyBtn.disabled = false;
        this.viewCollectionBtn.disabled = false;
    }

    disableButtons() {
        this.startJourneyBtn.disabled = true;
        this.viewCollectionBtn.disabled = true;
    }

    async startJourney() {
        try {
            // Sign a message to verify wallet ownership
            const message = `Welcome to Mystic Tarot NFT!\nPlease sign this message to begin your journey.\n\nTimestamp: ${Date.now()}`;
            this.showLoading('Verifying wallet ownership...');
            
            const signature = await this.web3Client.signMessage(message);
            
            // Store the signature in sessionStorage for the quiz page
            sessionStorage.setItem('walletSignature', signature);
            sessionStorage.setItem('walletAddress', this.web3Client.address);
            
            // Redirect to the quiz page
            window.location.href = '/tarot_quiz.html';
        } catch (error) {
            console.error('Failed to start journey:', error);
            alert('Failed to verify wallet ownership. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    async viewCollection() {
        if (!this.web3Client.address) {
            alert('Please connect your wallet first');
            return;
        }
        
        try {
            this.showLoading('Loading your collection...');
            // Redirect to collection page with address parameter
            window.location.href = `/collection.html?address=${this.web3Client.address}`;
        } catch (error) {
            console.error('Failed to view collection:', error);
            alert('Failed to load collection. Please try again.');
            this.hideLoading();
        }
    }

    showLoading(message) {
        this.loadingMessage.textContent = message;
        this.loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
