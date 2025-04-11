// main.ts
import { createAppKit } from '@reown/appkit'
import { mainnet, arbitrum } from '@reown/appkit/networks'
import { WagmiAdapter } from '@reown/appkit-adapter-wagmi'

// 1. Get a project ID at https://cloud.reown.com
const projectId = '1039c3b9fdb89a8fba67a0983f403d22'

export const networks = [mainnet, arbitrum]

// 2. Set up Wagmi adapter
const wagmiAdapter = new WagmiAdapter({
  projectId,
  networks
})

// 3. Configure the metadata
const metadata = {
  name: 'tarot',
  description: 'AppKit Example',
  url: 'https://reown.com/appkit',
  icons: ['https://assets.reown.com/reown-profile-pic.png']
}

// 3. Create the modal
const modal = createAppKit({
  adapters: [wagmiAdapter],
  networks: [mainnet, arbitrum],
  metadata,
  projectId,
  features: {
    analytics: true
  }
})

// 4. Set up UI elements
const startJourneyBtn = document.getElementById('startJourneyBtn') as HTMLButtonElement
const viewCollectionBtn = document.getElementById('viewCollectionBtn') as HTMLButtonElement

if (!startJourneyBtn || !viewCollectionBtn) {
  console.error('Required UI elements not found')
  throw new Error('Required UI elements not found')
}

// 5. Handle wallet connection state
modal.subscribeState((state) => {
  const isConnected = state.isConnected
  // Only show the collection button when wallet is connected
  viewCollectionBtn.style.display = isConnected ? 'block' : 'none'
})

// 6. Handle button clicks
startJourneyBtn.addEventListener('click', () => {
  window.location.href = '/personality_test.html'
})

viewCollectionBtn.addEventListener('click', async () => {
  const state = await modal.getState()
  if (state.isConnected) {
    window.location.href = '/collection.html'
  } else {
    modal.open()
  }
})

// Export for use in other modules
export { modal }
