import { modal } from './main'

interface CardInfo {
    name: string;
    image_path: string;
    orientation: string;
    meanings: {
        general: string;
        career: string;
        love: string;
        spirituality: string;
    };
}

interface ReadingResult {
    mbti_type: string;
    personality: {
        description: string;
        strengths: string[];
        weaknesses: string[];
    };
    tarot_info: {
        major_arcana: string;
        major_arcana_image: string;
        orientation: string;
        specific_meanings: {
            general: string;
            career: string;
            love: string;
            spirituality: string;
        };
    };
    minor_arcana: CardInfo[];
    can_mint: boolean;
}

// Get results from URL parameters
const urlParams = new URLSearchParams(window.location.search);
const resultData = JSON.parse(decodeURIComponent(urlParams.get('result') || '{}'));

function displayResults(result: ReadingResult) {
    // Display MBTI and personality info
    const mbtiTypeElement = document.getElementById('mbtiType');
    const personalityDescElement = document.getElementById('personalityDesc');
    if (mbtiTypeElement) mbtiTypeElement.textContent = `Your MBTI Type: ${result.mbti_type}`;
    if (personalityDescElement) personalityDescElement.textContent = result.personality.description;

    // Display Major Arcana
    const majorArcanaImg = document.getElementById('majorArcanaImg') as HTMLImageElement;
    const majorArcanaName = document.getElementById('majorArcanaName');
    const majorArcanaMeaning = document.getElementById('majorArcanaMeaning');
    
    if (majorArcanaImg) majorArcanaImg.src = result.tarot_info.major_arcana_image;
    if (majorArcanaName) majorArcanaName.textContent = result.tarot_info.major_arcana;
    if (majorArcanaMeaning) majorArcanaMeaning.textContent = result.tarot_info.specific_meanings.general;

    // Display Minor Arcana
    const minorArcanaContainer = document.getElementById('minorArcanaContainer');
    if (minorArcanaContainer) {
        minorArcanaContainer.innerHTML = result.minor_arcana
            .map(card => `
                <div class="card">
                    <img src="${card.image_path}" alt="${card.name}">
                    <div class="card-info">
                        <h4>${card.name}</h4>
                        <p>${card.meanings.general}</p>
                    </div>
                </div>
            `).join('');
    }

    // Show/hide mint section based on wallet connection
    const mintSection = document.getElementById('mintSection');
    if (mintSection) {
        mintSection.style.display = result.can_mint ? 'block' : 'none';
    }
}

// Handle minting
const mintBtn = document.getElementById('mintBtn');
if (mintBtn) {
    mintBtn.addEventListener('click', async () => {
        const state = await modal.getState();
        if (!state.isConnected) {
            modal.open();
            return;
        }
        // TODO: Implement minting logic
    });
}

// Handle saving via email
const saveBtn = document.getElementById('saveBtn');
const emailInput = document.getElementById('emailInput') as HTMLInputElement;
if (saveBtn && emailInput) {
    saveBtn.addEventListener('click', async () => {
        const email = emailInput.value;
        if (!email) {
            alert('Please enter your email address');
            return;
        }
        try {
            const response = await fetch('/api/save-reading', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    result: resultData
                })
            });
            if (response.ok) {
                alert('Reading saved! Check your email.');
            } else {
                throw new Error('Failed to save reading');
            }
        } catch (error) {
            alert('Error saving reading. Please try again.');
        }
    });
}

// Handle sharing
const shareBtn = document.getElementById('shareBtn');
if (shareBtn) {
    shareBtn.addEventListener('click', () => {
        if (navigator.share) {
            navigator.share({
                title: 'My Tarot Reading',
                text: `Check out my personalized tarot reading! I'm a ${resultData.mbti_type} personality type.`,
                url: window.location.href
            }).catch(console.error);
        } else {
            // Fallback for browsers that don't support sharing
            const shareUrl = window.location.href;
            navigator.clipboard.writeText(shareUrl).then(() => {
                alert('Link copied to clipboard!');
            });
        }
    });
}

// Display results when page loads
if (resultData) {
    displayResults(resultData);
}
