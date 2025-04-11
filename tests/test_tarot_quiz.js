// test_tarot_quiz.js
describe('TarotQuiz', () => {
    let quiz;
    let mockFetch;

    // Mock HTML structure
    const setupDOM = () => {
        document.body.innerHTML = `
            <div class="quiz-container">
                <div id="progress"></div>
                <div id="questions-container"></div>
                <div id="result"></div>
                <div class="loading">
                    <p id="loadingMessage"></p>
                </div>
                <span id="walletAddress"></span>
            </div>
        `;
    };

    beforeEach(() => {
        setupDOM();
        
        // Mock sessionStorage
        const mockSessionStorage = {
            getItem: jest.fn(),
            setItem: jest.fn(),
            clear: jest.fn()
        };
        Object.defineProperty(window, 'sessionStorage', {
            value: mockSessionStorage
        });

        // Mock fetch
        mockFetch = jest.fn();
        global.fetch = mockFetch;
        
        quiz = new TarotQuiz();
    });

    afterEach(() => {
        jest.clearAllMocks();
        document.body.innerHTML = '';
    });

    describe('Wallet Authentication', () => {
        it('should redirect to index if wallet data is missing', () => {
            window.sessionStorage.getItem.mockReturnValue(null);
            
            const mockLocation = { href: '' };
            Object.defineProperty(window, 'location', {
                value: mockLocation,
                writable: true
            });

            quiz.checkWalletAuth();
            expect(window.location.href).toBe('/index.html');
        });

        it('should display wallet address when authenticated', () => {
            const mockAddress = '0x1234567890123456789012345678901234567890';
            window.sessionStorage.getItem
                .mockReturnValueOnce(mockAddress) // walletAddress
                .mockReturnValueOnce('signature'); // walletSignature

            quiz.checkWalletAuth();

            const walletDisplay = document.getElementById('walletAddress');
            expect(walletDisplay.textContent).toBe('0x1234...7890');
            expect(walletDisplay.style.display).toBe('inline');
        });
    });

    describe('Question Loading', () => {
        const mockQuestions = {
            questions: [
                {
                    text: 'Question 1',
                    options: [
                        { text: 'Option 1', score: { 'E': 2 } },
                        { text: 'Option 2', score: { 'I': 2 } }
                    ]
                }
            ]
        };

        beforeEach(() => {
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockQuestions)
            });
        });

        it('should load questions successfully', async () => {
            await quiz.loadQuestions();
            expect(quiz.questions).toEqual(mockQuestions.questions);
            expect(quiz.totalQuestions).toBe(mockQuestions.questions.length);
        });

        it('should handle question loading error', async () => {
            mockFetch.mockRejectedValueOnce(new Error('Failed to load'));
            const consoleSpy = jest.spyOn(console, 'error');
            
            await quiz.loadQuestions();
            
            expect(consoleSpy).toHaveBeenCalled();
            expect(quiz.questions).toBeUndefined();
        });
    });

    describe('Answer Handling', () => {
        beforeEach(() => {
            quiz.questions = [{
                text: 'Question 1',
                options: [
                    { text: 'Option 1', score: { 'E': 2 } },
                    { text: 'Option 2', score: { 'I': 2 } }
                ]
            }];
            quiz.totalQuestions = 1;
        });

        it('should store answer and move to next question', async () => {
            await quiz.handleAnswer(0);
            expect(quiz.answers[0]).toBe(0);
        });

        it('should calculate results when all questions answered', async () => {
            const mockResult = {
                mbti_type: 'INTJ',
                personality: { name: 'Test', description: 'Test' },
                tarot_info: {
                    major_arcana: 'The Hermit',
                    orientation: 'Upright',
                    specific_meanings: ['Meaning 1']
                }
            };

            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResult)
            });

            await quiz.handleAnswer(0);
            
            expect(mockFetch).toHaveBeenCalledWith('/api/calculate-result', expect.any(Object));
            expect(document.getElementById('result').style.display).toBe('block');
        });

        it('should handle calculation error', async () => {
            mockFetch.mockRejectedValueOnce(new Error('Calculation failed'));
            const consoleSpy = jest.spyOn(console, 'error');
            
            await quiz.handleAnswer(0);
            
            expect(consoleSpy).toHaveBeenCalled();
        });
    });

    describe('Navigation', () => {
        beforeEach(() => {
            quiz.questions = [
                { text: 'Question 1' },
                { text: 'Question 2' }
            ];
            quiz.totalQuestions = 2;
        });

        it('should move to next question', () => {
            quiz.currentQuestionIndex = 0;
            quiz.nextQuestion();
            expect(quiz.currentQuestionIndex).toBe(1);
        });

        it('should move to previous question', () => {
            quiz.currentQuestionIndex = 1;
            quiz.previousQuestion();
            expect(quiz.currentQuestionIndex).toBe(0);
        });

        it('should not go past last question', () => {
            quiz.currentQuestionIndex = 1;
            quiz.nextQuestion();
            expect(quiz.currentQuestionIndex).toBe(1);
        });

        it('should not go before first question', () => {
            quiz.currentQuestionIndex = 0;
            quiz.previousQuestion();
            expect(quiz.currentQuestionIndex).toBe(0);
        });
    });

    describe('Progress Tracking', () => {
        it('should update progress bar correctly', () => {
            quiz.totalQuestions = 4;
            quiz.currentQuestionIndex = 1;
            
            quiz.updateProgress();
            
            const progress = document.getElementById('progress');
            expect(progress.style.width).toBe('50%');
        });
    });

    describe('Quiz Reset', () => {
        it('should reset quiz state correctly', () => {
            quiz.currentQuestionIndex = 5;
            quiz.answers = [0, 1, 2];
            
            quiz.restartQuiz();
            
            expect(quiz.currentQuestionIndex).toBe(0);
            expect(quiz.answers).toEqual([]);
            expect(document.querySelector('.quiz-container').style.display).toBe('block');
            expect(document.getElementById('result').style.display).toBe('none');
        });
    });
});
