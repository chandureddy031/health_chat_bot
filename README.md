# Healthcare Chatbot

AI-powered healthcare chatbot with user authentication and conversation management.

## Features

- ✅ User registration and authentication (JWT)
- ✅ Secure password hashing
- ✅ AI-powered chat using Groq LLM
- ✅ Conversation history management
- ✅ Session-based chat storage
- ✅ Modern, responsive UI
- ✅ Real-time chat interface

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- MongoDB (Database)
- JWT (Authentication)
- Groq API (LLM)
- Bcrypt (Password hashing)

**Frontend:**
- HTML5, CSS3, JavaScript
- Jinja2 templates
- Responsive design

## Installation

### Prerequisites
- Python 3.8+
- MongoDB Atlas account (or local MongoDB)
- Groq API key

### Setup

1. **Clone or create the project structure:**
```bash
mkdir healthcare_chatbot
cd healthcare_chatbot
```

2. **Create all files** as provided in the file structure.

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
- The `.env` file is already configured with your credentials
- **IMPORTANT:** Never commit `.env` to version control

5. **Run the application:**
```bash
python -m backend.main
```

Or using uvicorn directly:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the application:**
```
http://localhost:8000
```

## Usage

1. **Sign Up:** Create a new account at `/signup`
2. **Sign In:** Login with your credentials at `/signin`
3. **Chat:** Start chatting with the AI healthcare assistant
4. **History:** View and manage your chat sessions in the sidebar

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Login user

### Chat
- `POST /api/chat/message` - Send message and get response
- `GET /api/chat/sessions` - Get all user sessions
- `GET /api/chat/session/{id}` - Get specific session
- `DELETE /api/chat/session/{id}` - Delete session

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Secure HTTP-only approach
- Input validation
- CORS protection

## Project Structure

