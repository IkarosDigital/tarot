// test_web3_client.js
describe('Web3Client', () => {
    let web3Client;
    let mockEthereum;

    beforeEach(() => {
        // Mock ethereum provider
        mockEthereum = {
            request: jest.fn(),
            on: jest.fn(),
            removeListener: jest.fn(),
        };
        global.window = {
            ethereum: mockEthereum
        };
        web3Client = new Web3Client();
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('init()', () => {
        it('should successfully connect to wallet', async () => {
            const mockAddress = '0x1234567890123456789012345678901234567890';
            mockEthereum.request.mockResolvedValueOnce([mockAddress]);

            const address = await web3Client.init();

            expect(address).toBe(mockAddress);
            expect(web3Client.isConnected).toBe(true);
            expect(web3Client.address).toBe(mockAddress);
            expect(mockEthereum.request).toHaveBeenCalledWith({
                method: 'eth_requestAccounts'
            });
        });

        it('should throw error if MetaMask is not installed', async () => {
            delete global.window.ethereum;

            await expect(web3Client.init()).rejects.toThrow(
                'Please install MetaMask to use this application'
            );
        });

        it('should handle rejected wallet connection', async () => {
            mockEthereum.request.mockRejectedValueOnce(new Error('User rejected'));

            await expect(web3Client.init()).rejects.toThrow('User rejected');
            expect(web3Client.isConnected).toBe(false);
        });
    });

    describe('disconnect()', () => {
        it('should properly disconnect wallet', () => {
            web3Client.provider = 'provider';
            web3Client.signer = 'signer';
            web3Client.address = 'address';
            web3Client.isConnected = true;

            const mockHandleDisconnect = jest.fn();
            web3Client.handleDisconnect = mockHandleDisconnect;

            web3Client.disconnect();

            expect(web3Client.provider).toBeNull();
            expect(web3Client.signer).toBeNull();
            expect(web3Client.address).toBeNull();
            expect(web3Client.isConnected).toBe(false);
            expect(mockHandleDisconnect).toHaveBeenCalled();
        });
    });

    describe('signMessage()', () => {
        it('should successfully sign message', async () => {
            const mockMessage = 'Test message';
            const mockSignature = '0xsignature';
            web3Client.isConnected = true;
            web3Client.signer = {
                signMessage: jest.fn().mockResolvedValueOnce(mockSignature)
            };

            const signature = await web3Client.signMessage(mockMessage);

            expect(signature).toBe(mockSignature);
            expect(web3Client.signer.signMessage).toHaveBeenCalledWith(mockMessage);
        });

        it('should throw error if wallet is not connected', async () => {
            web3Client.isConnected = false;

            await expect(web3Client.signMessage('test')).rejects.toThrow(
                'Wallet not connected'
            );
        });

        it('should handle signing error', async () => {
            web3Client.isConnected = true;
            web3Client.signer = {
                signMessage: jest.fn().mockRejectedValueOnce(new Error('Signing failed'))
            };

            await expect(web3Client.signMessage('test')).rejects.toThrow('Signing failed');
        });
    });

    describe('Event handlers', () => {
        it('should handle account changes', async () => {
            const mockAddress = '0x1234567890123456789012345678901234567890';
            mockEthereum.request.mockResolvedValueOnce([mockAddress]);
            await web3Client.init();

            const mockNewAddress = '0x0987654321098765432109876543210987654321';
            const accountsChangedCallback = mockEthereum.on.mock.calls.find(
                call => call[0] === 'accountsChanged'
            )[1];

            accountsChangedCallback([mockNewAddress]);
            expect(web3Client.address).toBe(mockNewAddress);
        });

        it('should handle disconnect on empty accounts', async () => {
            const mockAddress = '0x1234567890123456789012345678901234567890';
            mockEthereum.request.mockResolvedValueOnce([mockAddress]);
            await web3Client.init();

            const accountsChangedCallback = mockEthereum.on.mock.calls.find(
                call => call[0] === 'accountsChanged'
            )[1];

            accountsChangedCallback([]);
            expect(web3Client.isConnected).toBe(false);
            expect(web3Client.address).toBeNull();
        });
    });
});
