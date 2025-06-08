// static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    const chatOutput = document.getElementById('chat-output');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    
    // Nuevos elementos para la subida de archivos
    const uploadFileButton = document.getElementById('upload-file-button');
    const fileInput = document.getElementById('file-input');
    const fileDisplayArea = document.getElementById('file-display-area');
    let selectedFile = null; // Variable para almacenar el archivo seleccionado

    // Función para añadir mensajes al chat
    function addMessage(text, sender) {
    	const messageDiv = document.createElement('div');
    	messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'ai-message');
    
    	const paragraph = document.createElement('p');
    	if (sender === 'ai') {
        	paragraph.innerHTML = text;
    	} else {
        	paragraph.textContent = text;
    	}
    	messageDiv.appendChild(paragraph);
    
    	chatOutput.appendChild(messageDiv);
    	chatOutput.scrollTop = chatOutput.scrollHeight;
	}

    // Función para mostrar el indicador de carga
    function showLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        loadingDiv.classList.add('message', 'ai-message', 'loading-indicator');
        loadingDiv.id = 'loading-indicator';
        
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

    // --- Lógica para la subida de archivos ---
    if (uploadFileButton && fileInput && fileDisplayArea) { // Asegurarse de que los elementos existen
        uploadFileButton.addEventListener('click', () => {
            fileInput.click(); // Activa el input de archivo oculto
        });

        fileInput.addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                selectedFile = file;
                fileDisplayArea.innerHTML = `
                    <span>${file.name}</span>
                    <button id="remove-file-button" class="remove-file-btn" title="Quitar archivo">×</button>
                `;
                // Añadir event listener al botón de quitar archivo
                document.getElementById('remove-file-button').addEventListener('click', () => {
                    selectedFile = null;
                    fileInput.value = ''; // Importante para permitir seleccionar el mismo archivo de nuevo
                    fileDisplayArea.innerHTML = '';
                });
            } else { // Si el usuario cancela la selección
                selectedFile = null;
                fileDisplayArea.innerHTML = '';
            }
        });
    }
    // --- Fin de la lógica para la subida de archivos ---

    async function handleSendMessage() {
        const question = userInput.value.trim();
        
        // No enviar si no hay pregunta Y no hay archivo.
        // O ajusta esta lógica si quieres permitir enviar solo un archivo sin pregunta.
        if (!question && !selectedFile) {
            userInput.focus(); // Devuelve el foco si no hay nada que enviar
            return;
        }

        // 1. Mostrar mensaje del usuario en el chat
        // Si hay un archivo, se podría añadir una nota al mensaje del usuario.
        let userMessageText = question;
        if (selectedFile && question) {
            userMessageText = `${question} (Archivo adjunto: ${selectedFile.name})`;
        } else if (selectedFile && !question) {
            userMessageText = `Archivo adjunto: ${selectedFile.name}`;
        }
        addMessage(userMessageText, 'user');
        
        userInput.value = ''; // Limpiar el input de texto
        userInput.focus();

        // 2. Mostrar indicador de carga
        showLoadingIndicator();

        // 3. Preparar datos para enviar (FormData para archivos)
        const formData = new FormData();
        formData.append('question', question); // La pregunta de texto (puede estar vacía)
        
        if (selectedFile) {
            formData.append('file', selectedFile, selectedFile.name); // El archivo
        }

        try {
            // 4. Enviar pregunta y/o archivo al backend
            const response = await fetch('/ask', {
                method: 'POST',
                // NO establezcas 'Content-Type': 'application/json' cuando uses FormData.
                // El navegador lo configurará automáticamente a 'multipart/form-data'
                // con el 'boundary' correcto.
                body: formData,
            });

            // 5. Quitar indicador de carga
            removeLoadingIndicator();

            // Limpiar el archivo seleccionado después de un envío exitoso o fallido (controlado por el servidor)
            if (selectedFile) {
                selectedFile = null;
                fileInput.value = ''; 
                fileDisplayArea.innerHTML = '';
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ answer: "Error al procesar la respuesta del servidor." }));
                addMessage(`Error: ${errorData.answer || response.statusText}`, 'ai');
                return;
            }

            const data = await response.json();
            
            // 6. Mostrar respuesta de la IA
            if (data.answer) {
                addMessage(data.answer, 'ai');
            } else if (data.error) {
                addMessage(`Error de la IA: ${data.error}`, 'ai');
            } else {
                addMessage("No se recibió una respuesta válida.", 'ai');
            }

        } catch (error) {
            // 7. Quitar indicador de carga y mostrar error de red/fetch
            removeLoadingIndicator();
            if (selectedFile) { // Limpiar también en caso de error de red
                selectedFile = null;
                fileInput.value = '';
                fileDisplayArea.innerHTML = '';
            }
            console.error('Error al enviar mensaje:', error);
            addMessage('Hubo un problema al conectar con el servidor. Inténtalo de nuevo.', 'ai');
        }
    }

    sendButton.addEventListener('click', handleSendMessage);

    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSendMessage();
        }
    });
});