// API Base URL
const API_BASE = window.location.origin;

// State
let currentSessionId = null;
let sessions = [];
let documents = [];

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        console.error('No token found, redirecting to signin');
        window.location.href = '/signin';
        return false;
    }
    return token;
}

// API Headers with auth
function getHeaders() {
    const token = checkAuth();
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// PDF Functions
async function loadDocuments() {
    try {
        console.log('Loading documents...');
        const response = await fetch(`${API_BASE}/api/pdf/documents`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/signin';
            return;
        }
        
        if (response.ok) {
            documents = await response.json();
            console.log('Documents loaded:', documents.length);
            renderDocuments();
        }
    } catch (error) {
        console.error('Load documents error:', error);
    }
}

function renderDocuments() {
    const documentsList = document.getElementById('documentsList');
    
    if (documents.length === 0) {
        documentsList.innerHTML = '<div class="empty-documents">No documents uploaded yet</div>';
        return;
    }
    
    documentsList.innerHTML = documents.map(doc => `
        <div class="document-item">
            <div>
                <div class="document-name" title="${doc.filename}">📄 ${doc.filename}</div>
                <div class="document-info">${doc.chunks_count} chunks</div>
            </div>
            <button class="document-delete" onclick="deleteDocument('${doc.id}')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" 
                          stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
        </div>
    `).join('');
}

async function uploadPDF(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Show upload progress
        const documentsList = document.getElementById('documentsList');
        documentsList.insertAdjacentHTML('afterbegin', `
            <div class="upload-progress" id="uploadProgress">
                <div class="upload-progress-bar">
                    <div class="upload-progress-fill" style="width: 50%"></div>
                </div>
                <div class="upload-progress-text">Uploading ${file.name}...</div>
            </div>
        `);
        
        const response = await fetch(`${API_BASE}/api/pdf/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${checkAuth()}`
            },
            body: formData
        });
        
        // Remove progress indicator
        document.getElementById('uploadProgress')?.remove();
        
        if (response.ok) {
            const data = await response.json();
            console.log('PDF uploaded:', data);
            alert(`✅ ${data.filename} uploaded! Processed ${data.chunks_count} chunks.`);
            await loadDocuments();
        } else {
            const error = await response.json();
            alert(`❌ Upload failed: ${error.detail}`);
        }
    } catch (error) {
        document.getElementById('uploadProgress')?.remove();
        console.error('Upload error:', error);
        alert('❌ Upload failed. Check console for details.');
    }
}

async function deleteDocument(documentId) {
    if (!confirm('Delete this document? It will no longer be used for answers.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/pdf/document/${documentId}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (response.ok) {
            console.log('Document deleted');
            await loadDocuments();
        } else {
            const error = await response.json();
            alert(`❌ Delete failed: ${error.detail}`);
        }
    } catch (error) {
        console.error('Delete document error:', error);
    }
}

// Chat Functions (keep existing functions)
async function loadSessions() {
    try {
        console.log('Loading sessions...');
        const response = await fetch(`${API_BASE}/api/chat/sessions`, {
            headers: getHeaders()
        });
        
        console.log('Sessions response status:', response.status);
        
        if (response.status === 401) {
            console.error('Unauthorized - token expired or invalid');
            alert('Your session has expired. Please login again.');
            localStorage.removeItem('token');
            window.location.href = '/signin';
            return;
        }
        
        if (response.ok) {
            sessions = await response.json();
            console.log('Sessions loaded:', sessions.length);
            renderSessions();
        } else {
            console.error('Failed to load sessions:', await response.text());
        }
    } catch (error) {
        console.error('Load sessions error:', error);
    }
}

function renderSessions() {
    const sessionsList = document.getElementById('sessionsList');
    
    if (sessions.length === 0) {
        sessionsList.innerHTML = '<div class="empty-sessions">No chat history yet.<br>Start a new conversation!</div>';
        return;
    }
    
    sessionsList.innerHTML = sessions.map(session => `
        <div class="session-item ${session.id === currentSessionId ? 'active' : ''}" 
             onclick="loadSession('${session.id}')">
            <span class="session-title">${session.title}</span>
            <button class="session-delete" onclick="deleteSession(event, '${session.id}')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" 
                          stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
        </div>
    `).join('');
}

async function loadSession(sessionId) {
    console.log('Loading session:', sessionId);
    currentSessionId = sessionId;
    renderSessions();
    
    try {
        const response = await fetch(`${API_BASE}/api/chat/session/${sessionId}`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            const session = await response.json();
            console.log('Session loaded with', session.messages.length, 'messages');
            renderMessages(session.messages);
        } else {
            console.error('Failed to load session:', await response.text());
        }
    } catch (error) {
        console.error('Load session error:', error);
    }
}

async function deleteSession(event, sessionId) {
    event.stopPropagation();
    
    if (!confirm('Delete this conversation?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/chat/session/${sessionId}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (response.ok) {
            console.log('Session deleted:', sessionId);
            if (currentSessionId === sessionId) {
                currentSessionId = null;
                clearMessages();
            }
            await loadSessions();
        } else {
            console.error('Delete failed:', await response.text());
        }
    } catch (error) {
        console.error('Delete session error:', error);
    }
}

function renderMessages(messages) {
    const container = document.getElementById('messagesContainer');
    const welcomeMsg = document.getElementById('welcomeMessage');
    
    if (welcomeMsg) {
        welcomeMsg.style.display = 'none';
    }
    
    container.innerHTML = messages.map(msg => createMessageHTML(msg)).join('');
    scrollToBottom();
}

function createMessageHTML(message) {
    const time = new Date(message.timestamp).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const avatar = message.role === 'user' ? '👤' : '🤖';
    
    // Convert markdown-style bold to HTML
    let content = escapeHtml(message.content);
    content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return `
        <div class="message ${message.role}">
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text">${content}</div>
                <div class="message-time">${time}</div>
            </div>
        </div>
    `;
}

function addMessage(role, content) {
    const container = document.getElementById('messagesContainer');
    const welcomeMsg = document.getElementById('welcomeMessage');
    
    if (welcomeMsg) {
        welcomeMsg.style.display = 'none';
    }
    
    const messageHTML = createMessageHTML({
        role,
        content,
        timestamp: new Date().toISOString()
    });
    
    container.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
}

function showTyping() {
    const container = document.getElementById('messagesContainer');
    const typingHTML = `
        <div class="message assistant" id="typingIndicator">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', typingHTML);
    scrollToBottom();
}

function hideTyping() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

async function sendMessage(message) {
    console.log('Sending message:', message);
    console.log('Current session ID:', currentSessionId);
    
    addMessage('user', message);
    showTyping();
    
    const sendBtn = document.getElementById('sendBtn');
    const messageInput = document.getElementById('messageInput');
    sendBtn.disabled = true;
    
    try {
        const requestBody = {
            message,
            session_id: currentSessionId
        };
        
        console.log('Request body:', requestBody);
        
        const response = await fetch(`${API_BASE}/api/chat/message`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(requestBody)
        });
        
        console.log('Response status:', response.status);
        
        hideTyping();
        
        if (response.ok) {
            const data = await response.json();
            console.log('Response data:', data);
            addMessage('assistant', data.response);
            
            if (!currentSessionId) {
                currentSessionId = data.session_id;
                console.log('New session created:', currentSessionId);
                await loadSessions();
            }
        } else {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            
            if (response.status === 401) {
                alert('Your session has expired. Please login again.');
                localStorage.removeItem('token');
                window.location.href = '/signin';
            } else {
                addMessage('assistant', `❌ Sorry, I encountered an error: ${errorText}`);
            }
        }
    } catch (error) {
        hideTyping();
        console.error('Send message error:', error);
        addMessage('assistant', `❌ Network error: ${error.message}`);
    } finally {
        sendBtn.disabled = false;
        messageInput.value = '';
        messageInput.style.height = 'auto';
    }
}

function clearMessages() {
    const container = document.getElementById('messagesContainer');
    const welcomeMsg = document.getElementById('welcomeMessage');
    
    container.innerHTML = '';
    if (welcomeMsg) {
        container.appendChild(welcomeMsg);
        welcomeMsg.style.display = 'block';
    }
}

function newChat() {
    console.log('Starting new chat');
    currentSessionId = null;
    clearMessages();
    renderSessions();
    document.getElementById('messageInput').focus();
}

function scrollToBottom() {
    const container = document.getElementById('messagesContainer');
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function logout() {
    console.log('Logging out');
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    window.location.href = '/signin';
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('show');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Chat page loaded');
    console.log('Token exists:', !!localStorage.getItem('token'));
    
    checkAuth();
    
    // Load sessions and documents
    loadSessions();
    loadDocuments();
    
    // PDF upload handler
    document.getElementById('pdfUpload').addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            uploadPDF(file);
            e.target.value = ''; // Reset input
        }
    });
    
    // Chat form
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        console.log('Form submitted');
        const message = messageInput.value.trim();
        console.log('Message:', message);
        if (message) {
            sendMessage(message);
        } else {
            console.warn('Empty message, not sending');
        }
    });
    
    messageInput.addEventListener('input', () => autoResize(messageInput));
    
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            console.log('Enter pressed, submitting form');
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
    
    document.getElementById('newChatBtn').addEventListener('click', newChat);
    document.getElementById('logoutBtn').addEventListener('click', logout);
    document.getElementById('toggleSidebar').addEventListener('click', toggleSidebar);
    
    console.log('All event listeners attached');
});