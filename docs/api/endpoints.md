# API Endpoints Reference

Complete reference for all API endpoints with request/response examples, parameters, and error handling.

## 🏠 Health & Status Endpoints

### GET /health
**Description**: Application health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "service": "interview-api",
  "timestamp": "2024-11-10T10:30:00Z"
}
```

**Status Codes**:
- `200`: Service is healthy
- `503`: Service is unhealthy

---

### GET /
**Description**: Root endpoint with API information

**Response**:
```json
{
  "message": "Interview API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

## 🎬 Film Endpoints

### GET /api/v1/films/
**Description**: Retrieve a list of films with pagination and filtering

**Query Parameters**:
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records (default: 100, max: 1000)
- `category` (str, optional): Filter by category name (case insensitive, supports partial matching)
- `year` (int, optional): Filter by release year
- `rating` (str, optional): Filter by MPAA rating

**Example Request**:
```bash
# Case insensitive and partial matching
curl -X GET "http://localhost:8000/api/v1/films/?skip=0&limit=10&category=action"
curl -X GET "http://localhost:8000/api/v1/films/?skip=0&limit=10&category=Act"
```

**Response**:
```json
[
  {
    "film_id": 1,
    "title": "ACADEMY DINOSAUR",
    "description": "A Epic Drama of a Feminist And a Mad Scientist...",
    "release_year": 2006,
    "rental_duration": 6,
    "rental_rate": 0.99,
    "length": 86,
    "replacement_cost": 20.99,
    "rating": "PG",
    "special_features": ["Deleted Scenes", "Behind the Scenes"],
    "streaming_available": false
  }
]
```

**Status Codes**:
- `200`: Success
- `422`: Invalid query parameters

---

### GET /api/v1/films/{film_id}
**Description**: Retrieve a specific film by ID

**Path Parameters**:
- `film_id` (int, required): Film identifier

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/films/1"
```

**Response**:
```json
{
  "film_id": 1,
  "title": "ACADEMY DINOSAUR",
  "description": "A Epic Drama of a Feminist And a Mad Scientist...",
  "release_year": 2006,
  "rental_duration": 6,
  "rental_rate": 0.99,
  "length": 86,
  "replacement_cost": 20.99,
  "rating": "PG",
  "special_features": ["Deleted Scenes", "Behind the Scenes"],
  "streaming_available": false
}
```

**Status Codes**:
- `200`: Film found
- `404`: Film not found

---

### POST /api/v1/films/
**Description**: Create a new film

**Request Body**:
```json
{
  "title": "New Amazing Film",
  "description": "An incredible story of adventure and discovery",
  "release_year": 2024,
  "rental_duration": 3,
  "rental_rate": 4.99,
  "length": 120,
  "replacement_cost": 19.99,
  "rating": "PG-13",
  "special_features": ["Commentary", "Deleted Scenes"],
  "streaming_available": true
}
```

**Response**:
```json
{
  "film_id": 1001,
  "title": "New Amazing Film",
  "description": "An incredible story of adventure and discovery",
  "release_year": 2024,
  "rental_duration": 3,
  "rental_rate": 4.99,
  "length": 120,
  "replacement_cost": 19.99,
  "rating": "PG-13",
  "special_features": ["Commentary", "Deleted Scenes"],
  "streaming_available": true
}
```

**Status Codes**:
- `201`: Film created successfully
- `422`: Validation error

---

### PUT /api/v1/films/{film_id}
**Description**: Update an existing film

**Path Parameters**:
- `film_id` (int, required): Film identifier

**Request Body**: Same as POST (all fields optional for updates)

**Status Codes**:
- `200`: Film updated successfully
- `404`: Film not found
- `422`: Validation error

---

### DELETE /api/v1/films/{film_id}
**Description**: Delete a film

**Path Parameters**:
- `film_id` (int, required): Film identifier

**Response**: `204 No Content`

**Status Codes**:
- `204`: Film deleted successfully
- `404`: Film not found

---

### GET /api/v1/films/search
**Description**: Search films by title, description, or other criteria

**Query Parameters**:
- `q` (str, required): Search query
- `limit` (int, optional): Maximum results (default: 10)

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/films/search?q=dinosaur&limit=5"
```

**Response**:
```json
[
  {
    "film_id": 1,
    "title": "ACADEMY DINOSAUR",
    "description": "A Epic Drama of a Feminist And a Mad Scientist...",
    "release_year": 2006,
    "relevance_score": 0.95
  }
]
```

## 📂 Category Endpoints

### GET /api/v1/categories/
**Description**: Retrieve all film categories

**Response**:
```json
[
  {
    "category_id": 1,
    "name": "Action",
    "last_update": "2024-11-10T10:30:00Z"
  },
  {
    "category_id": 2,
    "name": "Animation",
    "last_update": "2024-11-10T10:30:00Z"
  }
]
```

---

### GET /api/v1/categories/{category_id}
**Description**: Retrieve a specific category

**Path Parameters**:
- `category_id` (int, required): Category identifier

**Response**:
```json
{
  "category_id": 1,
  "name": "Action",
  "last_update": "2024-11-10T10:30:00Z",
  "film_count": 64
}
```

---

### POST /api/v1/categories/
**Description**: Create a new category

**Request Body**:
```json
{
  "name": "Documentary"
}
```

**Response**:
```json
{
  "category_id": 17,
  "name": "Documentary",
  "last_update": "2024-11-10T10:30:00Z"
}
```

## 🏪 Rental Endpoints

### GET /api/v1/rentals/
**Description**: Retrieve rental records with filtering

**Query Parameters**:
- `customer_id` (int, optional): Filter by customer
- `film_id` (int, optional): Filter by film
- `active_only` (bool, optional): Show only active rentals
- `skip` (int, optional): Pagination offset
- `limit` (int, optional): Pagination limit

**Response**:
```json
[
  {
    "rental_id": 1,
    "rental_date": "2024-11-01T14:30:00Z",
    "inventory_id": 367,
    "customer_id": 130,
    "return_date": null,
    "staff_id": 1,
    "film_title": "ACADEMY DINOSAUR",
    "customer_name": "Charlotte Hunter",
    "is_overdue": false
  }
]
```

---

### POST /api/v1/rentals/
**Description**: Create a new rental

**Request Body**:
```json
{
  "inventory_id": 367,
  "customer_id": 130,
  "staff_id": 1
}
```

**Response**:
```json
{
  "rental_id": 16050,
  "rental_date": "2024-11-10T10:30:00Z",
  "inventory_id": 367,
  "customer_id": 130,
  "return_date": null,
  "staff_id": 1,
  "due_date": "2024-11-13T10:30:00Z"
}
```

---

### PUT /api/v1/rentals/{rental_id}/return
**Description**: Process rental return

**Path Parameters**:
- `rental_id` (int, required): Rental identifier

**Response**:
```json
{
  "rental_id": 16050,
  "return_date": "2024-11-10T15:45:00Z",
  "late_fee": 0.00,
  "status": "returned"
}
```

## 👥 Customer Endpoints

### GET /api/v1/customers/
**Description**: Retrieve customer list

**Query Parameters**:
- `active_only` (bool, optional): Show only active customers
- `search` (str, optional): Search by name or email
- `skip` (int, optional): Pagination offset
- `limit` (int, optional): Pagination limit

**Response**:
```json
[
  {
    "customer_id": 1,
    "first_name": "Mary",
    "last_name": "Smith",
    "email": "mary.smith@sakilacustomer.org",
    "active": true,
    "create_date": "2024-01-01T00:00:00Z",
    "rental_count": 32
  }
]
```

---

### GET /api/v1/customers/{customer_id}
**Description**: Retrieve customer details with rental history

**Path Parameters**:
- `customer_id` (int, required): Customer identifier

**Response**:
```json
{
  "customer_id": 1,
  "first_name": "Mary",
  "last_name": "Smith",
  "email": "mary.smith@sakilacustomer.org",
  "active": true,
  "create_date": "2024-01-01T00:00:00Z",
  "address": {
    "address": "1913 Hanoi Way",
    "city": "Sasebo",
    "country": "Japan",
    "postal_code": "35200"
  },
  "rental_history": [
    {
      "rental_id": 1,
      "film_title": "ACADEMY DINOSAUR",
      "rental_date": "2024-11-01T14:30:00Z",
      "return_date": "2024-11-05T10:15:00Z"
    }
  ]
}
```

## 🤖 AI Endpoints

### POST /api/v1/ai/handoff
**Description**: Interact with AI agents for film recommendations and general questions

**Request Body**:
```json
{
  "question": "Tell me about action movies from 2010",
  "context": {
    "user_preferences": ["action", "thriller"],
    "previous_rentals": [1, 5, 10]
  }
}
```

**Response**:
```json
{
  "answer": "Based on your interest in action movies from 2010, I found several great options in our database. Here are some recommendations:\n\n1. **Inception** - A mind-bending thriller about dream infiltration\n2. **The Expendables** - Action-packed ensemble cast\n3. **Iron Man 2** - Superhero action sequel\n\nWould you like more details about any of these films?",
  "agent": "SearchAgent",
  "confidence": 0.92,
  "sources": ["film_database"],
  "films_found": [
    {
      "film_id": 428,
      "title": "Inception",
      "relevance": 0.95
    }
  ]
}
```

**Status Codes**:
- `200`: Response generated successfully
- `422`: Invalid question format
- `500`: AI service error

---

### POST /api/v1/ai/search
**Description**: AI-powered film search with natural language

**Request Body**:
```json
{
  "query": "funny movies about talking animals",
  "limit": 5,
  "include_recommendations": true
}
```

**Response**:
```json
{
  "results": [
    {
      "film_id": 15,
      "title": "CHICKEN RUN",
      "description": "A Touching Display of a Monkey And a Feminist...",
      "relevance_score": 0.89,
      "match_reasons": ["animals", "comedy"]
    }
  ],
  "recommendations": [
    {
      "film_id": 25,
      "title": "FINDING NEMO",
      "reason": "Similar theme with animal characters"
    }
  ],
  "total_found": 12,
  "search_interpretation": "Looking for comedy films featuring animal characters"
}
```

---

### POST /api/v1/ai/recommend
**Description**: Get personalized film recommendations

**Request Body**:
```json
{
  "customer_id": 130,
  "preferences": {
    "genres": ["Action", "Sci-Fi"],
    "min_rating": "PG-13",
    "max_length": 150
  },
  "count": 5
}
```

**Response**:
```json
{
  "recommendations": [
    {
      "film_id": 428,
      "title": "Inception",
      "recommendation_score": 0.94,
      "reasons": [
        "Matches your sci-fi preference",
        "Similar to your previous rentals",
        "Highly rated by similar customers"
      ]
    }
  ],
  "explanation": "These recommendations are based on your rental history, preferences, and similar customer behavior."
}
```

## 🚨 Error Response Format

### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "release_year"],
      "msg": "ensure this value is greater than or equal to 1900",
      "type": "value_error.number.not_ge",
      "ctx": {"limit_value": 1900}
    }
  ]
}
```

### Not Found Error (404)
```json
{
  "detail": "Film with id 9999 not found"
}
```

### Authentication Error (401)
```json
{
  "detail": "Could not validate credentials"
}
```

### Rate Limit Error (429)
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "retry_after": 60
}
```

## 📊 Response Headers

### Common Headers
```http
Content-Type: application/json
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Response-Time: 45ms
```

### Pagination Headers
```http
X-Total-Count: 1000
X-Page: 1
X-Per-Page: 50
X-Total-Pages: 20
Link: </api/v1/films/?page=2>; rel="next", </api/v1/films/?page=20>; rel="last"
```

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 🔧 Request Examples

### Using curl
```bash
# Get films with filtering (case insensitive category)
curl -X GET "http://localhost:8000/api/v1/films/?category=action&year=2010" \
  -H "Accept: application/json"

# Create a new film
curl -X POST "http://localhost:8000/api/v1/films/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Film",
    "description": "A great new film",
    "release_year": 2024,
    "rating": "PG-13"
  }'

# AI interaction
curl -X POST "http://localhost:8000/api/v1/ai/handoff" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Recommend some sci-fi movies"
  }'
```

### Using Python httpx
```python
import httpx
import asyncio

async def get_films():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/films/")
        return response.json()

async def ask_ai(question: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/ai/handoff",
            json={"question": question}
        )
        return response.json()

# Usage
films = asyncio.run(get_films())
ai_response = asyncio.run(ask_ai("Tell me about action movies"))
```

This comprehensive endpoint reference provides all the information needed to integrate with the Interview API effectively.
