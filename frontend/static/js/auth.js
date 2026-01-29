// API Base URL
const API_BASE = window.location.origin;

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
    
    setTimeout(() => {
        errorDiv.classList.remove('show');
    }, 5000);
}

// Sign Up Handler
function initSignUp() {
    const form = document.getElementById('signupForm');
    const submitBtn = document.getElementById('submitBtn');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        // Validation
        if (password !== confirmPassword) {
            showError('Passwords do not match');
            return;
        }
        
        if (password.length < 6) {
            showError('Password must be at least 6 characters');
            return;
        }
        
        // Disable button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating account...';
        
        try {
            const response = await fetch(`${API_BASE}/api/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert('Account created successfully! Please sign in.');
                window.location.href = '/signin';
            } else {
                showError(data.detail || 'Registration failed');
            }
        } catch (error) {
            showError('Network error. Please try again.');
            console.error('Signup error:', error);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Sign Up';
        }
    });
}

// Sign In Handler
function initSignIn() {
    const form = document.getElementById('signinForm');
    const submitBtn = document.getElementById('submitBtn');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        
        // Disable button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Signing in...';
        
        try {
            const response = await fetch(`${API_BASE}/api/auth/signin`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Store token
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('userEmail', email);
                
                // Redirect to chat
                window.location.href = '/chat';
            } else {
                showError(data.detail || 'Sign in failed');
            }
        } catch (error) {
            showError('Network error. Please try again.');
            console.error('Signin error:', error);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Sign In';
        }
    });
}