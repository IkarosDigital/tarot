// JavaScript for Tarot Quiz
class TarotQuiz {
    constructor() {
        this.currentQuestionIndex = 0;
        this.answers = [];
        this.totalQuestions = 20;
        this.walletAddress = null;
        this.walletSignature = null;
        this.initializeElements();
        this.checkWalletAuth();
    }

    initializeElements() {
        // Quiz elements
        this.quizContainer = document.querySelector('.quiz-container');
        this.resultContainer = document.getElementById('result');
        this.progressBar = document.getElementById('progress');
        this.questionsContainer = document.getElementById('questions-container');
        this.loadingOverlay = document.querySelector('.loading');
        this.loadingMessage = document.getElementById('loadingMessage');
        this.walletAddressDisplay = document.getElementById('walletAddress');
    }

    async checkWalletAuth() {
        // Get wallet data from session storage
        this.walletAddress = sessionStorage.getItem('walletAddress');
        this.walletSignature = sessionStorage.getItem('walletSignature');

        if (!this.walletAddress || !this.walletSignature) {
            // Redirect to landing page if not authenticated
            window.location.href = '/index.html';
            return;
        }

        // Display wallet address
        this.walletAddressDisplay.style.display = 'inline';
        this.walletAddressDisplay.textContent = `${this.walletAddress.slice(0, 6)}...${this.walletAddress.slice(-4)}`;

        // Show quiz and load first question
        this.quizContainer.style.display = 'block';
        await this.loadQuestions();
        this.showQuestion(0);
    }

    async loadQuestions() {
        try {
            const response = await fetch('/api/questions');
            if (!response.ok) {
                throw new Error('Failed to load questions');
            }
            const data = await response.json();
            this.questions = data.questions;
            this.totalQuestions = this.questions.length;
        } catch (error) {
            console.error('Error loading questions:', error);
            this.handleError(error);
        }
    }

    async handleAnswer(optionIndex) {
        try {
            // Add answer to our array
            this.answers[this.currentQuestionIndex] = optionIndex;
            
            // If all questions are answered, calculate result
            if (this.answers.length === this.totalQuestions && !this.answers.includes(undefined)) {
                const response = await fetch('/api/calculate-result', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        answers: this.answers,
                        walletAddress: this.walletAddress,
                        walletSignature: this.walletSignature,
                        template_id: 'classic'
                    })
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.details || 'Error calculating results');
                }

                const result = await response.json();
                this.displayResults(result);
            } else {
                // Move to next question if not at the end
                if (this.currentQuestionIndex < this.totalQuestions - 1) {
                    this.currentQuestionIndex++;
                    this.showQuestion(this.currentQuestionIndex);
                }
            }
        } catch (error) {
            console.error('Error calculating results:', error);
            this.handleError(error);
        }
    }

    displayResults(result) {
        const { mbti_type, personality, tarot_info } = result;
        
        const resultHTML = `
            <div class="result-container">
                <h2>Your Mystic Personality: ${mbti_type}</h2>
                <div class="personality-info">
                    <h3>${personality.name}</h3>
                    <p>${personality.description}</p>
                </div>
                <div class="tarot-info">
                    <h3>Your Tarot Alignment</h3>
                    <div class="card-display">
                        <img src="${tarot_info.major_arcana_image}" alt="${tarot_info.major_arcana}" class="tarot-card">
                        <h4>${tarot_info.major_arcana}</h4>
                        <p class="card-orientation">Card Orientation: ${tarot_info.orientation}</p>
                    </div>
                    <div class="card-meanings">
                        <h4>Card Meanings</h4>
                        <ul>
                            ${tarot_info.specific_meanings.map(meaning => `<li>${meaning}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                ${result.minor_arcana.length > 0 ? `
                    <div class="minor-arcana">
                        <h3>Supporting Cards</h3>
                        <div class="minor-cards">
                            ${result.minor_arcana.map(card => `
                                <div class="minor-card">
                                    <img src="${card.image_path}" alt="${card.name}" class="tarot-card">
                                    <h4>${card.name}</h4>
                                    <p>Suite: ${card.suite}</p>
                                    <p>Orientation: ${card.orientation}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                <div class="result-actions">
                    <button onclick="window.location.href='/collection.html'" class="btn-primary">View Collection</button>
                    <button onclick="quiz.restartQuiz()" class="btn-secondary">Take Quiz Again</button>
                </div>
            </div>
        `;
        
        this.resultContainer.innerHTML = resultHTML;
        this.resultContainer.style.display = 'block';
        this.quizContainer.style.display = 'none';
    }

    handleError(error) {
        const errorContainer = document.createElement('div');
        errorContainer.className = 'error-message';
        errorContainer.textContent = error.message || 'An error occurred';
        document.body.appendChild(errorContainer);
        
        setTimeout(() => {
            errorContainer.remove();
        }, 5000);
    }

    showQuestion(index) {
        if (!this.questions) return;
        
        const question = this.questions[index];
        const questionHTML = `
            <div class="question-container">
                <h2>${question.text}</h2>
                <div class="options">
                    ${question.options.map((option, i) => `
                        <button class="option" onclick="quiz.handleAnswer(${i})">${option.text}</button>
                    `).join('')}
                </div>
            </div>
        `;
        
        this.questionsContainer.innerHTML = questionHTML;
        this.updateProgress();
    }

    updateProgress() {
        const progressPercentage = ((this.currentQuestionIndex + 1) / this.totalQuestions) * 100;
        this.progressBar.style.width = `${progressPercentage}%`;
    }

    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.showQuestion(this.currentQuestionIndex);
        }
    }

    nextQuestion() {
        if (this.currentQuestionIndex < this.totalQuestions - 1) {
            this.currentQuestionIndex++;
            this.showQuestion(this.currentQuestionIndex);
        }
    }

    restartQuiz() {
        this.currentQuestionIndex = 0;
        this.answers = [];
        this.showQuestion(0);
        this.quizContainer.style.display = 'block';
        this.resultContainer.style.display = 'none';
    }

    showLoading(message) {
        this.loadingMessage.textContent = message;
        this.loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }
}

// Initialize quiz when page loads
let quiz;
document.addEventListener('DOMContentLoaded', () => {
    quiz = new TarotQuiz();
});
