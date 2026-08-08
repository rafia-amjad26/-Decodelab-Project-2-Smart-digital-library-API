# DecodeLabs Full Stack Development - Project 2
## Smart Digital Library API

Backend API & Full Stack Web App built with Python & Flask for DecodeLabs Industrial Training.

🌐 **Live Demo:** [https://decodelab-smart-digital-library.vercel.app](https://decodelab-smart-digital-library.vercel.app)

---

### Key Concepts Implemented
- **IPO Model:** Structured Input (JSON body), Processing (Flask logic), Output (JSON response)
- **Gatekeeper Rule:** Syntactic & Semantic validation on incoming requests
- **RESTful Naming Conventions:** Resource nouns used (`/api/v1/books`)
- **Semantic Status Codes:** Proper HTTP responses (`200`, `201`, `204`, `400`, `404`)

---

### API Endpoints

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/books` | Fetch all books | `200 OK` |
| **POST** | `/api/v1/books` | Add new book | `201 Created` / `400 Bad Request` |
| **PUT** | `/api/v1/books/<id>` | Update book details | `200 OK` / `400 Bad Request` |
| **PATCH**| `/api/v1/books/<id>/status` | Toggle Borrow/Available status | `200 OK` |
| **DELETE**| `/api/v1/books/<id>` | Remove book | `204 No Content` / `404 Not Found` |
| **POST** | `/api/v1/auth/login` | User Authentication | `200 OK` / `401 Unauthorized` |

---

# 📖 Smart Digital Library Management System

A modern, fast, and feature-rich Web Application built using **Python (Flask)** and **SQLite**. It allows users to manage library books, search and filter by category, export reports, and handles multi-user authentication.

## ✨ Features

* 🔐 **User Authentication & Role-Based Access Control**
  * **Admin:** Full access to Add, Edit, Delete, and Manage books.
  * **Student:** View catalogue, search, and Borrow/Return books.
* 📚 **Complete CRUD Operations:** Add new books, update details, or delete records.
* 🔍 **Advanced Filters:** Search books by title/author, category, and availability status.
* 📊 **Dashboard Analytics:** Live stats for total, available, and borrowed books.
* 📥 **Export Data:** Download library records as **CSV/Excel** or print clean **PDF reports**.
* 🔔 **Interactive UI:** Smooth SweetAlert2 notifications and toast alerts.

---

## 🛠️ Tech Stack

* **Backend:** Python (Flask), SQLite3
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API)
* **UI Libraries:** SweetAlert2
* **Deployment:** Vercel

---

## 🔑 Default Credentials for Testing

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` |
| **Student** | `student` | `student123` |

---

### Request Body Example (POST `/api/v1/books`)
```json
{
  "title": "Design Patterns",
  "author": "Erich Gamma",
  "category": "Software Engineering"
}
