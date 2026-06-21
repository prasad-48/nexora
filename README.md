# Nexora — Electronics E-commerce with AI Shopping Assistant

A full-stack e-commerce application for electronics, built as a portfolio project to demonstrate full-stack development and AI integration skills as part of a transition into AI/ML engineering roles.

**Live demo:** _add your deployed link here once hosted_

---

## Features

- 🛍️ **Product catalog** — browse, search, and filter electronics by category, price, and brand
- 🔐 **Authentication** — JWT-based register/login with secure password hashing (bcrypt)
- 🛒 **Cart & checkout** — persistent cart, stock validation, order placement
- 📦 **Order history** — track past orders and their status
- 🤖 **AI shopping assistant** — chatbot powered by Google Gemini that recommends products and answers order questions, grounded in the live product catalog and the logged-in user's order history

---

## Tech Stack

**Frontend**
- HTML, Tailwind CSS, vanilla JavaScript (no framework)

**Backend**
- FastAPI (Python)
- SQLite + SQLAlchemy ORM
- JWT authentication (HTTPBearer)

**AI**
- Google Gemini API (`gemini-2.5-flash-lite`)

---

## Architecture

```
Browser (HTML/Tailwind/JS)
        │  HTTP / JSON
        ▼
FastAPI backend
  ├── /api/auth      — register, login, current user
  ├── /api/products   — list, search, filter, CRUD (admin)
  ├── /api/orders     — place order, order history
  └── /api/chat       — AI assistant (catalog + order-aware)
        │  SQLAlchemy ORM
        ▼
SQLite database
        │
        ▼
Google Gemini API (chat completions)
```

---

## Running locally

### Prerequisites
- Python 3.11+
- A free [Google Gemini API key](https://aistudio.google.com)

### Backend setup

```bash
git clone https://github.com/your-username/nexora.git
cd nexora
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GEMINI_API_KEY=your_gemini_api_key_here
APP_NAME=Nexora
DEBUG=True
```

Seed the database with sample products:

```bash
python -m backend.seed_data
```

Start the backend:

```bash
uvicorn backend.main:app --reload --port 8001
```

API docs available at `http://127.0.0.1:8001/docs`

### Frontend setup

Open `frontend/index.html` with a local server (e.g. VS Code's Live Server extension). Opening it directly as a `file://` URL will not work correctly due to browser security restrictions on cross-origin requests.

---

## What I learned building this

- Designing a relational schema (users, products, orders, order items) and working with SQLAlchemy relationships
- Implementing JWT authentication from scratch — password hashing, token generation/validation, protected routes
- Building a context-aware AI feature: injecting live product and order data into prompts so the chatbot gives grounded, accurate answers instead of generic responses
- Debugging real-world issues: CORS, trailing-slash redirects stripping auth headers, global scope collisions between scripts, bcrypt version compatibility
- Structuring a project for maintainability with environment-based configuration and clear separation between routers, models, and schemas

---

## Project status

Built as a learning project while transitioning into AI/ML engineering roles. Feedback welcome!