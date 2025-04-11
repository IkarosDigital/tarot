import { walletState } from './main'

// UI Elements
const startJourneyBtn = document.getElementById('startJourneyBtn') as HTMLButtonElement
const viewCollectionBtn = document.getElementById('viewCollectionBtn') as HTMLButtonElement
const walletAddressSpan = document.getElementById('walletAddress') as HTMLSpanElement
const loadingOverlay = document.getElementById('loadingOverlay') as HTMLDivElement
const loadingMessage = document.getElementById('loadingMessage') as HTMLParagraphElement
const networkModalBtn = document.getElementById('open-network-modal') as HTMLButtonElement

// Update UI based on wallet state
function updateUI() {
    if (walletState.isConnected && walletState.isVerified) {
        // Show connected wallet address
        walletAddressSpan.textContent = `${walletState.address?.slice(0, 6)}...${walletState.address?.slice(-4)}`
        walletAddressSpan.style.display = 'block'
        
        // Enable buttons
        startJourneyBtn.disabled = false
        viewCollectionBtn.disabled = false
        networkModalBtn.style.display = 'block'
    } else {
        // Reset UI to disconnected state
        walletAddressSpan.textContent = ''
        walletAddressSpan.style.display = 'none'
        
        // Disable buttons
        startJourneyBtn.disabled = true
        viewCollectionBtn.disabled = true
        networkModalBtn.style.display = 'none'
    }
}

// Show/hide loading overlay
function setLoading(isLoading: boolean, message: string = 'Loading...') {
    loadingOverlay.style.display = isLoading ? 'flex' : 'none'
    loadingMessage.textContent = message
}

// Handle start journey button click
startJourneyBtn.addEventListener('click', async () => {
    if (!walletState.isVerified) {
        alert('Please connect your wallet first')
        return
    }
    
    try {
        setLoading(true, 'Starting your journey...')
        // Add your journey start logic here
        
    } catch (error) {
        console.error('Failed to start journey:', error)
        alert('Failed to start journey. Please try again.')
    } finally {
        setLoading(false)
    }
})

// Handle view collection button click
viewCollectionBtn.addEventListener('click', async () => {
    if (!walletState.isVerified) {
        alert('Please connect your wallet first')
        return
    }
    
    try {
        setLoading(true, 'Loading your collection...')
        const response = await fetch(`/api/collection/${walletState.address}`)
        
        if (response.ok) {
            const collection = await response.json()
            // Add your collection display logic here
            console.log('Collection:', collection)
        } else {
            throw new Error('Failed to load collection')
        }
    } catch (error) {
        console.error('Failed to load collection:', error)
        alert('Failed to load collection. Please try again.')
    } finally {
        setLoading(false)
    }
})

// Watch for wallet state changes
Object.defineProperty(walletState, 'isVerified', {
    set(value) {
        this._isVerified = value
        updateUI()
    },
    get() {
        return this._isVerified
    }
})

// Initial UI update
updateUI()
