// static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    const chatOutput = document.getElementById('chat-output');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Función para añadir mensajes al chat
    function addMessage(text, sender) {
    	const messageDiv = document.createElement('div');
    	messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'ai-message');
    
    	const paragraph = document.createElement('p');
    	if (sender === 'ai') {
        	paragraph.innerHTML = text; // <--- CAMBIO AQUÍ para mensajes de la IA
    	} else {
        	paragraph.textContent = text; // Mantenemos textContent para mensajes del usuario (más seguro)
    	}
    	messageDiv.appendChild(paragraph);
    
    	chatOutput.appendChild(messageDiv);
    	chatOutput.scrollTop = chatOutput.scrollHeight; // Auto-scroll hacia abajo
	}

    // Función para mostrar el indicador de carga
    function showLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        loadingDiv.classList.add('message', 'ai-message', 'loading-indicator'); // Reutilizamos estilo de ai-message
        loadingDiv.id = 'loading-indicator'; // Para poder quitarlo luego
        
        const paragraph = document.createElement('p');
        paragraph.textContent = 'Gemini está pensando... 🤔';
        loadingDiv.appendChild(paragraph);
        
        chatOutput.appendChild(loadingDiv);
        chatOutput.scrollTop = chatOutput.scrollHeight;
    }

    // Función para quitar el indicador de carga
    function removeLoadingIndicator() {
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
    }

    async function handleSendMessage() {
        const question = userInput.value.trim();
        if (!question) return; // No enviar si está vacío

        // 1. Mostrar pregunta del usuario en el chat
        addMessage(question, 'user');
        userInput.value = ''; // Limpiar el input
        userInput.focus(); // Devolver el foco al input

        // 2. Mostrar indicador de carga
        showLoadingIndicator();

        try {
            // 3. Enviar pregunta al backend
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question }), // 'question' debe coincidir con lo que espera el backend
            });

            // 4. Quitar indicador de carga
            removeLoadingIndicator();

            if (!response.ok) {
                // Si la respuesta del servidor no es OK (ej. error 500)
                const errorData = await response.json().catch(() => ({ answer: "Error al procesar la respuesta del servidor." }));
                addMessage(`Error: ${errorData.answer || response.statusText}`, 'ai');
                return;
            }

            const data = await response.json();
            
            // 5. Mostrar respuesta de la IA
            if (data.answer) {
                addMessage(data.answer, 'ai');
            } else if (data.error) { // Si el backend envía un error específico
                addMessage(`Error de la IA: ${data.error}`, 'ai');
            } else {
                addMessage("No se recibió una respuesta válida.", 'ai');
            }

        } catch (error) {
            // 6. Quitar indicador de carga (por si acaso) y mostrar error de red/fetch
            removeLoadingIndicator();
            console.error('Error al enviar mensaje:', error);
            addMessage('Hubo un problema al conectar con el servidor. Inténtalo de nuevo.', 'ai');
        }
    }

    sendButton.addEventListener('click', handleSendMessage);

    userInput.addEventListener('keypress', (event) => {
        // Enviar con Enter (Shift+Enter para nueva línea)
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Evitar nueva línea en textarea
            handleSendMessage();
        }
    });

    // Mensaje inicial (opcional, ya lo tienes en el HTML, pero así se podría añadir dinámicamente)
    // addMessage("Hola 👋 ¿En qué puedo ayudarte hoy?", 'ai');
});