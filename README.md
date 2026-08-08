# DecodeLabs Full Stack Development - Project 2
## Smart Digital Library API

Backend API built with Python & Flask for DecodeLabs Industrial Training[cite: 1].

### Key Concepts Implemented
- **IPO Model:** Structured Input (JSON body), Processing (Flask logic), Output (JSON response)[cite: 1]
- **Gatekeeper Rule:** Syntactic & Semantic validation on incoming requests[cite: 1]
- **RESTful Naming Conventions:** Resource nouns used (`/api/v1/books`)[cite: 1]
- **Semantic Status Codes:** Proper HTTP responses (`200`, `201`, `204`, `400`, `404`)[cite: 1]

---

### API Endpoints

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/books` | Fetch all books | `200 OK` |
| **GET** | `/api/v1/books/<id>` | Fetch single book | `200 OK` / `404 Not Found` |
| **POST** | `/api/v1/books` | Add new book | `201 Created` / `400 Bad Request` |
| **DELETE**| `/api/v1/books/<id>` | Remove book | `204 No Content` / `404 Not Found` |

---

### Request Body Example (POST)
```json
{
  "title": "Design Patterns",
  "author": "Erich Gamma",
  "category": "Software Engineering"
}