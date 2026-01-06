/**
 * Cuestionario Clima Organizacional - Conversational Chat Interface
 * Interactive chat-style questionnaire flow
 */

// API Configuration - Uses relative URL so it works from any host
const API_BASE_URL = '';

// State Management
const state = {
    questions: [],
    responseOptions: [],
    currentQuestionIndex: 0,
    userResponses: {},
    respondentInfo: {
        name: null,
        email: null,
        department: null
    },
    conversationPhase: 'welcome', // welcome, info, questions, complete
    isTyping: false
};

// DOM Elements
const elements = {
    chatMessages: document.getElementById('chat-messages'),
    chatInputArea: document.getElementById('chat-input-area'),
    progressFill: document.getElementById('progress-fill'),
    progressText: document.getElementById('progress-text'),
    loadingOverlay: document.getElementById('loading'),
    toast: document.getElementById('toast'),
    restartBtn: document.getElementById('restart-btn')
};

// Avatar SVGs
const BOT_AVATAR = `
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
`;

const USER_AVATAR = `
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
    </svg>
`;

/**
 * Initialize the application
 */
async function init() {
    bindEvents();
    await loadQuestions();
    startConversation();
}

/**
 * Bind event listeners
 */
function bindEvents() {
    elements.restartBtn.addEventListener('click', restartConversation);
}

/**
 * Load questions from the API
 */
async function loadQuestions() {
    try {
        showLoading();

        // Fetch questions
        const questionsResponse = await fetch(`${API_BASE_URL}/api/questions`);
        if (!questionsResponse.ok) throw new Error('Failed to load questions');
        const questionsData = await questionsResponse.json();
        state.questions = questionsData.questions;

        // Fetch response options
        const optionsResponse = await fetch(`${API_BASE_URL}/api/options`);
        if (!optionsResponse.ok) throw new Error('Failed to load options');
        const optionsData = await optionsResponse.json();
        state.responseOptions = optionsData.options;

        hideLoading();
    } catch (error) {
        hideLoading();
        console.warn('Using default data - API not available:', error);
        useDefaultData();
    }
}

/**
 * Use default data when API is not available
 */
function useDefaultData() {
    state.questions = [
        { id: 1, text: "Dolores en el cuello y espalda o tensión muscular", category: "SÍNTOMAS FISIOLÓGICOS" },
        { id: 2, text: "Problemas gastrointestinales, úlcera péptica, acidez, problemas digestivos o del colon", category: "SÍNTOMAS FISIOLÓGICOS" },
        { id: 3, text: "Problemas respiratorios", category: "SÍNTOMAS FISIOLÓGICOS" },
        { id: 4, text: "Dolor de cabeza", category: "SÍNTOMAS FISIOLÓGICOS" },
        { id: 5, text: "Trastornos del sueño como somnolencia durante el día o desvelo en la noche", category: "SÍNTOMAS FISIOLÓGICOS" },
        { id: 6, text: "Palpitaciones en el pecho o problemas cardíacos", category: "SÍNTOMAS FISIOLÓGICOS" },
        { id: 7, text: "Cambios fuertes del apetito", category: "SÍNTOMAS FISIOLÓGICOS" },
        { id: 8, text: "Problemas relacionados con la función de los órganos genitales", category: "SÍNTOMAS FISIOLÓGICOS" },
        { id: 9, text: "Dificultad en las relaciones familiares", category: "SÍNTOMAS COMPORTAMENTALES" },
        { id: 10, text: "Dificultad para permanecer quieto o dificultad para iniciar actividades", category: "SÍNTOMAS COMPORTAMENTALES" },
        { id: 11, text: "Dificultad en las relaciones con otras personas", category: "SÍNTOMAS COMPORTAMENTALES" },
        { id: 12, text: "Sensación de aislamiento y desinterés", category: "SÍNTOMAS EMOCIONALES" },
        { id: 13, text: "Sentimiento de sobrecarga de trabajo", category: "SÍNTOMAS LABORALES" },
        { id: 14, text: "Dificultad para concentrarse, olvidos frecuentes", category: "SÍNTOMAS INTELECTUALES" },
        { id: 15, text: "Aumento en el número de accidentes de trabajo", category: "SÍNTOMAS LABORALES" },
        { id: 16, text: "Sentimiento de frustración", category: "SÍNTOMAS EMOCIONALES" },
        { id: 17, text: "Cansancio, tedio o desgano", category: "SÍNTOMAS EMOCIONALES" },
        { id: 18, text: "Disminución del rendimiento en el trabajo o poca creatividad", category: "SÍNTOMAS LABORALES" },
        { id: 19, text: "Deseo de no asistir al trabajo", category: "SÍNTOMAS LABORALES" },
        { id: 20, text: "Bajo compromiso o poco interés con lo que se hace", category: "SÍNTOMAS LABORALES" },
        { id: 21, text: "Dificultad para tomar decisiones", category: "SÍNTOMAS INTELECTUALES" },
        { id: 22, text: "Deseo de cambiar de empleo", category: "SÍNTOMAS LABORALES" },
        { id: 23, text: "Sentimiento de soledad y miedo", category: "SÍNTOMAS EMOCIONALES" },
        { id: 24, text: "Sentimiento de irritabilidad, actitudes y pensamientos negativos", category: "SÍNTOMAS EMOCIONALES" },
        { id: 25, text: "Sentimiento de angustia, preocupación o tristeza", category: "SÍNTOMAS EMOCIONALES" },
        { id: 26, text: "Consumo de drogas para aliviar la tensión o los nervios", category: "SÍNTOMAS COMPORTAMENTALES" },
        { id: 27, text: "Sentimientos de que no vale nada", category: "SÍNTOMAS EMOCIONALES" },
        { id: 28, text: "Consumo de bebidas alcohólicas o café o cigarrillo", category: "SÍNTOMAS COMPORTAMENTALES" },
        { id: 29, text: "Sentimiento de que está perdiendo la razón", category: "SÍNTOMAS EMOCIONALES" },
        { id: 30, text: "Comportamientos rígidos, obstinación o terquedad", category: "SÍNTOMAS COMPORTAMENTALES" },
        { id: 31, text: "Sensación de no poder manejar los problemas de la vida", category: "SÍNTOMAS EMOCIONALES" }
    ];

    state.responseOptions = [
        { value: 1, label: "Siempre" },
        { value: 2, label: "Casi siempre" },
        { value: 3, label: "A veces" },
        { value: 4, label: "Nunca" }
    ];
}

/**
 * Start the conversation flow
 */
function startConversation() {
    state.conversationPhase = 'welcome';
    updateProgress();
    showWelcomeMessage();
}

/**
 * Show welcome message
 */
async function showWelcomeMessage() {
    await addBotMessage(`
        <div class="welcome-content">
            <div class="welcome-emoji">🧘</div>
            <div class="welcome-title">¡Hola! Bienvenido al Cuestionario de Evaluación del Estrés</div>
            <div class="welcome-subtitle">Señala la frecuencia con que se te han presentado los siguientes malestares en los últimos tres meses.</div>
            <ul class="instructions-list">
                <li>Tus respuestas son confidenciales</li>
                <li>No hay respuestas correctas o incorrectas</li>
                <li>Solo tomará unos minutos</li>
            </ul>
        </div>
    `);

    showStartButton();
}

/**
 * Show start button
 */
function showStartButton() {
    elements.chatInputArea.innerHTML = `
        <button class="continue-btn" onclick="startQuestions()">
            <span>Comenzar Encuesta</span>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </button>
    `;
}

/**
 * Start the questions flow
 */
async function startQuestions() {
    await addUserMessage("¡Estoy listo para comenzar!");

    state.conversationPhase = 'info';

    await delay(500);
    await askForName();
}

/**
 * Ask for user's name
 */
async function askForName() {
    await addBotMessage("Primero, ¿podrías decirme tu nombre? <span style='color: var(--text-muted);'>(Opcional - puedes dejarlo en blanco)</span>");

    showTextInput('name', 'Tu nombre (opcional)', () => {
        const input = document.getElementById('text-input-name');
        state.respondentInfo.name = input.value.trim() || null;
        handleNameResponse();
    });
}

/**
 * Handle name response
 */
async function handleNameResponse() {
    if (state.respondentInfo.name) {
        await addUserMessage(state.respondentInfo.name);
        await delay(500);
        await addBotMessage(`¡Mucho gusto, ${state.respondentInfo.name}! 😊`);
    } else {
        await addUserMessage("Prefiero no decirlo");
        await delay(500);
        await addBotMessage("¡No hay problema! Tu privacidad es importante. 🔒");
    }

    await delay(500);
    await askForDepartment();
}

/**
 * Ask for department
 */
async function askForDepartment() {
    await addBotMessage("¿En qué departamento trabajas? <span style='color: var(--text-muted);'>(Opcional)</span>");

    showTextInput('department', 'Tu departamento (opcional)', () => {
        const input = document.getElementById('text-input-department');
        state.respondentInfo.department = input.value.trim() || null;
        handleDepartmentResponse();
    });
}

/**
 * Handle department response
 */
async function handleDepartmentResponse() {
    if (state.respondentInfo.department) {
        await addUserMessage(state.respondentInfo.department);
    } else {
        await addUserMessage("Prefiero no decirlo");
    }

    await delay(500);
    await addBotMessage("¡Perfecto! Ahora comenzaremos con las preguntas del cuestionario. 📝");
    await delay(800);
    await addBotMessage(`Son <strong>${state.questions.length} preguntas</strong> rápidas. Para cada una, selecciona la opción que mejor refleje tu opinión.`);

    await delay(1000);
    state.conversationPhase = 'questions';
    state.currentQuestionIndex = 0;
    showCurrentQuestion();
}

/**
 * Show current question
 */
async function showCurrentQuestion() {
    const question = state.questions[state.currentQuestionIndex];
    updateProgress();

    const questionMessage = `
        <div class="question-badge">Pregunta ${question.id} de ${state.questions.length}</div>
        <div class="category-badge">${question.category}</div>
        <div style="margin-top: 8px; font-size: 1.1rem;">${question.text}</div>
    `;

    await addBotMessage(questionMessage);
    showResponseOptions(question.id);
}

/**
 * Get emoji for response option value
 */
function getOptionEmoji(value, label) {
    // Map response values to appropriate emojis - Frecuencia de malestares
    // Mayor frecuencia = más estrés = emoji más preocupado
    const emojiMap = {
        1: '😰', // Siempre - muy estresado
        2: '😟', // Casi siempre - preocupado
        3: '😐', // A veces - neutral
        4: '😊'  // Nunca - tranquilo/feliz
    };
    return emojiMap[value] || '❓';
}

/**
 * Show response options for a question
 */
function showResponseOptions(questionId) {
    let optionsHTML = '<div class="options-container">';

    state.responseOptions.forEach((option, index) => {
        const emoji = getOptionEmoji(option.value, option.label);
        optionsHTML += `
            <button class="option-btn" onclick="selectOption(${questionId}, ${option.value}, '${option.label.replace(/'/g, "\\'")}')">
                <span class="option-emoji">${emoji}</span>
                <span class="option-text">${option.label}</span>
            </button>
        `;
    });

    optionsHTML += '</div>';
    elements.chatInputArea.innerHTML = optionsHTML;

    // Ensure options are visible by scrolling
    setTimeout(() => scrollToBottom(), 100);
}

/**
 * Handle option selection
 */
async function selectOption(questionId, value, label) {
    // Save response
    state.userResponses[questionId] = value;

    // Show user's choice
    await addUserMessage(label);

    // Move to next question or finish
    state.currentQuestionIndex++;

    if (state.currentQuestionIndex < state.questions.length) {
        await delay(600);
        showCurrentQuestion();
    } else {
        await delay(600);
        await finishQuestionnaire();
    }
}

/**
 * Finish the questionnaire
 */
async function finishQuestionnaire() {
    state.conversationPhase = 'complete';
    updateProgress();

    await addBotMessage("¡Excelente! Has completado todas las preguntas. 🎉");
    await delay(500);
    await addBotMessage("¿Listo para enviar tus respuestas?");

    showSubmitOptions();
}

/**
 * Show submit options
 */
function showSubmitOptions() {
    elements.chatInputArea.innerHTML = `
        <div class="submit-section">
            <button class="submit-btn" onclick="submitSurvey()">
                <span>Enviar Respuestas</span>
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
        </div>
    `;
}

/**
 * Submit the survey
 */
async function submitSurvey() {
    try {
        await addUserMessage("¡Enviar mis respuestas!");

        showLoading();

        // Prepare submission data
        const submissionData = {
            respondent_name: state.respondentInfo.name,
            respondent_email: state.respondentInfo.email,
            department: state.respondentInfo.department,
            responses: Object.entries(state.userResponses).map(([questionId, value]) => ({
                question_id: parseInt(questionId),
                response_value: value
            }))
        };

        // Submit to API
        const response = await fetch(`${API_BASE_URL}/api/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(submissionData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to submit survey');
        }

        const result = await response.json();

        hideLoading();
        await showSuccess(result.submission_id);

    } catch (error) {
        hideLoading();

        // If API is not available, simulate success
        if (error.message.includes('Failed to fetch')) {
            const mockId = 'LOCAL-' + Date.now();
            saveToLocalStorage();
            await showSuccess(mockId);
        } else {
            await addBotMessage(`❌ Error al enviar: ${error.message}. Por favor, intenta de nuevo.`);
            showSubmitOptions();
        }
    }
}

/**
 * Show success message
 */
async function showSuccess(submissionId) {
    await addBotMessage(`
        <div class="success-message">
            <div class="success-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.709 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13631 4.39828 5.49706C5.79935 3.85781 7.69279 2.71537 9.79619 2.24013C11.8996 1.7649 14.1003 1.98232 16.07 2.85999" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <div class="success-title">¡Encuesta Enviada!</div>
            <div class="success-text">Gracias por completar el cuestionario. Tu opinión es muy valiosa.</div>
            <div class="success-id">ID: ${submissionId}</div>
        </div>
    `);

    showToast('¡Encuesta enviada exitosamente!', 'success');

    elements.chatInputArea.innerHTML = `
        <button class="continue-btn" onclick="restartConversation()">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 4V10H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M23 20V14H17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M20.49 9C19.9828 7.56678 19.1209 6.28532 17.9845 5.27542C16.8482 4.26551 15.4745 3.55976 13.9917 3.22426C12.5089 2.88875 10.9652 2.93434 9.50481 3.35677C8.04437 3.77921 6.71475 4.56471 5.64 5.64L1 10M23 14L18.36 18.36C17.2853 19.4353 15.9556 20.2208 14.4952 20.6432C13.0348 21.0657 11.4911 21.1112 10.0083 20.7757C8.52547 20.4402 7.15183 19.7345 6.01547 18.7246C4.87912 17.7147 4.01717 16.4332 3.51 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>Realizar Nueva Encuesta</span>
        </button>
    `;
}

/**
 * Save responses to localStorage as fallback
 */
function saveToLocalStorage() {
    const savedResponses = JSON.parse(localStorage.getItem('surveyResponses') || '[]');
    savedResponses.push({
        id: 'LOCAL-' + Date.now(),
        timestamp: new Date().toISOString(),
        responses: state.userResponses,
        respondent: state.respondentInfo
    });
    localStorage.setItem('surveyResponses', JSON.stringify(savedResponses));
}

/**
 * Restart conversation
 */
function restartConversation() {
    // Reset state
    state.currentQuestionIndex = 0;
    state.userResponses = {};
    state.respondentInfo = { name: null, email: null, department: null };
    state.conversationPhase = 'welcome';

    // Clear messages
    elements.chatMessages.innerHTML = '';

    // Start fresh
    startConversation();
}

/**
 * Add a bot message to the chat
 */
async function addBotMessage(content) {
    // Show typing indicator
    showTypingIndicator();

    // Simulate typing delay (based on message length)
    const typingDelay = Math.min(1500, Math.max(500, content.length * 10));
    await delay(typingDelay);

    // Remove typing indicator
    removeTypingIndicator();

    // Add message
    const messageHTML = `
        <div class="message bot">
            <div class="message-avatar">${BOT_AVATAR}</div>
            <div class="message-bubble">
                <div class="message-text">${content}</div>
            </div>
        </div>
    `;

    elements.chatMessages.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
}

/**
 * Add a user message to the chat
 */
async function addUserMessage(content) {
    const messageHTML = `
        <div class="message user">
            <div class="message-avatar">${USER_AVATAR}</div>
            <div class="message-bubble">
                <div class="message-text">${content}</div>
            </div>
        </div>
    `;

    elements.chatMessages.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();

    // Clear input area temporarily
    elements.chatInputArea.innerHTML = '';
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    state.isTyping = true;
    const typingHTML = `
        <div class="message bot typing-message">
            <div class="message-avatar">${BOT_AVATAR}</div>
            <div class="message-bubble">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
    `;

    elements.chatMessages.insertAdjacentHTML('beforeend', typingHTML);
    scrollToBottomImmediate();
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator() {
    state.isTyping = false;
    const typingMessage = document.querySelector('.typing-message');
    if (typingMessage) {
        typingMessage.remove();
    }
}

/**
 * Show text input for open questions
 */
function showTextInput(fieldId, placeholder, onSubmit) {
    elements.chatInputArea.innerHTML = `
        <div class="text-input-container">
            <input 
                type="text" 
                id="text-input-${fieldId}" 
                class="text-input" 
                placeholder="${placeholder}"
                onkeydown="if(event.key === 'Enter') { event.preventDefault(); document.getElementById('send-btn-${fieldId}').click(); }"
            >
            <button id="send-btn-${fieldId}" class="send-btn" onclick="(${onSubmit.toString()})()">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
        </div>
    `;

    // Focus on the input
    setTimeout(() => {
        document.getElementById(`text-input-${fieldId}`).focus();
    }, 100);
}

/**
 * Update progress bar
 */
function updateProgress() {
    const total = state.questions.length;
    let current = 0;
    let text = '';

    if (state.conversationPhase === 'welcome' || state.conversationPhase === 'info') {
        current = 0;
        text = `Preparando cuestionario...`;
    } else if (state.conversationPhase === 'questions') {
        current = state.currentQuestionIndex;
        text = `Pregunta ${current + 1} de ${total}`;
    } else if (state.conversationPhase === 'complete') {
        current = total;
        text = `¡Completado!`;
    }

    const percentage = (current / total) * 100;
    elements.progressFill.style.width = `${percentage}%`;
    elements.progressText.textContent = text;
}

/**
 * Scroll to bottom of chat with smooth animation
 */
function scrollToBottom() {
    // Small delay to ensure content is rendered
    requestAnimationFrame(() => {
        elements.chatMessages.scrollTo({
            top: elements.chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    });
}

/**
 * Force immediate scroll (for typing indicator)
 */
function scrollToBottomImmediate() {
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

/**
 * Delay helper
 */
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Show loading overlay
 */
function showLoading() {
    elements.loadingOverlay.classList.remove('hidden');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    elements.loadingOverlay.classList.add('hidden');
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    elements.toast.className = `toast ${type}`;
    elements.toast.querySelector('.toast-message').textContent = message;
    elements.toast.classList.remove('hidden');

    // Auto hide after 3 seconds
    setTimeout(() => {
        elements.toast.classList.add('hidden');
    }, 3000);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
