# EventSphere – Agent-Based Event Management System

## 1. Project Overview

EventSphere is a web-based event management system developed using **FastAPI** and an agent-based architecture. It is designed to support event management activities such as user registration, event and venue management, ticket booking, QR-based check-in, and administrative operations.

The system provides different interfaces and access permissions for Attendees, Administrators, and Gate Staff.

## 2. Main Features

- User registration and login.
- Role-based access control for Attendees, Administrators, and Gate Staff.
- Event and venue management.
- Event browsing and ticket booking.
- Ticket capacity and overbooking validation.
- QR-based ticket check-in.
- Duplicate check-in prevention.
- Waitlist functionality.
- Venue hire request management.
- Administrative dashboard.
- REST API documentation using Swagger UI.

## 3. Technologies Used

| Area | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Database | SQLite (local), PostgreSQL (deployment) |
| ORM | SQLAlchemy |
| Frontend | HTML, CSS, JavaScript |
| Templates | Jinja2 |
| API Documentation | Swagger UI / OpenAPI |
| Testing | Pytest |
| Deployment | Render |
| Version Control | Git and GitHub |
| Agent Architecture | Python-based agents |

## 4. Agent-Based Architecture

The system includes the following agents:

1. **Venue Agent** – Handles venue availability-related operations.
2. **Booking Agent** – Checks venue availability during booking-related operations.
3. **Ticket Agent** – Handles ticket validation-related operations.
4. **Waitlist Agent** – Handles waitlist requests.
5. **Notification Agent** – Handles notification-related operations.

These agents are implemented as separate components to support the distribution of responsibilities within the system.

## 5. User Roles

| User Role | Main Responsibilities |
|---|---|
| Attendee | Register, log in, browse events, manage bookings and tickets, and access waitlist functionality. |
| Administrator | Access administrative functions and manage system operations. |
| Gate Staff | Scan and validate tickets and perform check-in operations. |

## 6. Project Structure

```text
EventSphere/
│
├── app/
│   ├── agents/
│   ├── database/
│   ├── routes/
│   ├── templates/
│   ├── static/
│   └── main.py
│
├── tests/
│   ├── test_agents.py
│   └── test_api.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

## 7. Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- pip

### Step 1: Clone the Repository

```bash
git clone https://github.com/AyodyaEkanayake/EventSphere.git
```

### Step 2: Navigate to the Project

```bash
cd EventSphere
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Configure Environment Variables

Create a `.env` file in the project root directory and configure the required environment variables.

Example:

```env
DATABASE_URL=your_database_connection_url
SECRET_KEY=your_secret_key
```

Use your own secure values. Do not commit the `.env` file to GitHub.

### Step 7: Run the Application

```bash
uvicorn app.main:app --reload
```

### Step 8: Access the Application

- Application: http://127.0.0.1:8000
- Login: http://127.0.0.1:8000/login
- Swagger API Documentation: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health

## 8. Testing

The project uses Pytest for automated testing.

Run all tests:

```bash
python -m pytest -v
```

Run agent tests:

```bash
python -m pytest -v tests/test_agents.py
```

### Test Results

The final local test execution completed with:

**18 passed, 1 warning**

The tests cover areas including:

- Agent operations.
- User registration and authentication.
- Role-based access control.
- Waitlist access permissions.
- Overbooking prevention.
- Duplicate ticket check-in prevention.

The warning reported during testing was non-fatal.

## 9. Deployment

The application backend is deployed using Render.

- **Live Application:** https://eventsphere-api-3mcn.onrender.com
- **API Documentation:** https://eventsphere-api-3mcn.onrender.com/docs
- **Health Check:** https://eventsphere-api-3mcn.onrender.com/health

The deployed application uses PostgreSQL, while the local development setup supports SQLite.

## 10. Limitations and Future Improvements

Potential future improvements include:

- Implementing a complete payment gateway integration.
- Extending booking cancellation and refund workflows.
- Improving automated venue hire decision-making.
- Enhancing agent-to-agent communication and proactive behaviour.
- Adding more comprehensive integration and deployment tests.
- Improving production monitoring and error handling.

## 11. Author

**Ayodya Ekanayake**

BSc (Hons) in Information Technology  
University of Vavuniya

GitHub: https://github.com/AyodyaEkanayake

---

*EventSphere – Agent-Based Event Management System*