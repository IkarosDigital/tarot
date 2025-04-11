class Web3Client {
    constructor() {
        this.provider = null;
        this.signer = null;
        this.address = null;
        this.isConnected = false;
    }

    async init() {
        // Check if MetaMask is installed
        if (typeof window.ethereum === 'undefined') {
            throw new Error('Please install MetaMask to use this application');
        }

        try {
            // Request account access
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            this.address = accounts[0];

            // Create ethers provider and signer
            this.provider = new ethers.providers.Web3Provider(window.ethereum);
            this.signer = this.provider.getSigner();
            this.isConnected = true;

            // Listen for account changes
            window.ethereum.on('accountsChanged', (accounts) => {
                if (accounts.length === 0) {
                    this.disconnect();
                } else {
                    this.address = accounts[0];
                    this.handleAccountChange(accounts[0]);
                }
            });

            return this.address;
        } catch (error) {
            console.error('Error connecting to wallet:', error);
            throw error;
        }
    }

    disconnect() {
        this.provider = null;
        this.signer = null;
        this.address = null;
        this.isConnected = false;
        this.handleDisconnect();
    }

    async signMessage(message) {
        if (!this.isConnected) {
            throw new Error('Wallet not connected');
        }

        try {
            const signature = await this.signer.signMessage(message);
            return signature;
        } catch (error) {
            console.error('Error signing message:', error);
            throw error;
        }
    }

    // Callback handlers - to be set by the main app
    handleAccountChange = (address) => {
        console.log('Account changed:', address);
    }

    handleDisconnect = () => {
        console.log('Wallet disconnected');
    }
}
