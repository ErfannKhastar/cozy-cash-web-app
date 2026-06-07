# ☕ CozyCash - Personal Finance & Expense Tracker

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

CozyCash is a full-stack, secure, and highly scalable personal finance web application designed to help users track their daily expenses, set monthly budgets, and analyze their spending habits through interactive charts.

> 💡 **Developer's Note:** > My primary focus in this project was engineering the **Backend Architecture, Database Design, and DevOps Infrastructure**. The User Interface (Frontend - HTML/CSS/JS) was developed with the assistance of AI tools to provide a complete and aesthetically pleasing user experience, allowing me to focus on core backend logic, security, and CI/CD automation.

---

## 🚀 Key Features

* **Secure Authentication:** JWT-based OAuth2 login and registration system.
* **Expense Management:** Full CRUD operations for daily transactions with category and date filtering.
* **Smart Budgeting:** Set monthly budget limits per category with visual progress bars and dynamic health statuses.
* **Interactive Dashboard:** Real-time analytics and data visualization using Chart.js (Spending Trends & Category Breakdowns).
* **Automated Infrastructure:** Multi-stage Docker builds with an intelligent entrypoint script (`start.sh`) for automatic database migrations.
* **Enterprise-Grade Testing:** Comprehensive Pytest suite utilizing transaction rollbacks for isolated and lightning-fast database testing.

---

## 🛠️ Tech Stack & Architecture

| Layer | Technologies & Tools | Description |
| :--- | :--- | :--- |
| **Backend** | Python, FastAPI, SQLAlchemy | Core API logic, routing, and ORM. |
| **Database** | PostgreSQL, Alembic | Relational data storage and automated schema migrations. |
| **Frontend** | HTML5, CSS3, Vanilla JS, Bootstrap 5 | Responsive UI, asynchronous API calls via Fetch API, and Jinja2 templating. |
| **Testing** | Pytest, HTTPX | E2E and integration tests with a dedicated test database environment. |
| **DevOps (CI/CD)** | Docker, Docker Compose, GitHub Actions | Containerization, environment overrides, and automated build/test/push pipelines. |
| **Server** | Uvicorn, Gunicorn | ASGI server for development and robust process management for production. |

---

## ⚙️ How It Works (Project Flow)

1. **Client-Side:** The user interacts with the UI. Vanilla JavaScript catches form submissions and sends asynchronous requests (`fetch`) to the FastAPI backend.
2. **Server-Side:** FastAPI receives the request, validates the payload using Pydantic schemas, and authenticates the user via JWT stored in `localStorage`.
3. **Database:** SQLAlchemy ORM executes the query against the PostgreSQL database.
4. **CI/CD Pipeline:** Every push to the `main` branch triggers a GitHub Action. A temporary PostgreSQL container is spun up, `pytest` runs the test suite, and if successful, a new Docker image is built and pushed to Docker Hub.

---

## 💻 Local Setup & Installation

Follow these steps to run the project locally using Docker.

### 1. Clone the Repository
```bash
git clone https://github.com/ErfannKhastar/cozy_cash_web_app.git
cd cozy_cash_web_app
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory and add the following parameters:
```env
# Database Configuration
DATABASE_USER=postgres
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=db
DATABASE_PORT=5432
DATABASE_NAME=expenses_tracker

# Security (JWT)
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Run with Docker Compose (Development)
The development environment uses `uvicorn` with auto-reload enabled.
```bash
docker compose up --build
```
*The `start.sh` script will automatically apply Alembic migrations to the database upon startup.*

### 4. Access the Application
* **Web App:** Navigate to `http://localhost:8000`
* **API Docs (Swagger UI):** Navigate to `http://localhost:8000/docs`

---

## 🌍 Production Deployment

For deploying to a live server, we use a Docker Compose override file (`docker-compose-prod.yml`) which switches the server to **Gunicorn** for better concurrency and sets restart policies.

```bash
docker compose -f docker-compose.yml -f docker-compose-prod.yml up -d
```
*Note: In the CI/CD pipeline, the production image is pulled directly from Docker Hub rather than building locally on the server.*

---

## 🧪 Running Tests

The test suite is designed to be completely isolated. It creates a separate database (`expenses_tracker_test`) and uses database transaction rollbacks to keep tests fast and prevent data leakage.

To run the tests inside the Docker container:
```bash
docker compose exec web pytest -v
```

---

## 👨‍💻 Author
**Erfan Khastar**
* GitHub: [@ErfannKhastar](https://github.com/ErfannKhastar)
* Role: Backend Developer & DevOps Engineer

---