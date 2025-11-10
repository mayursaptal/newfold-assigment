# API Overview

The Interview API provides a comprehensive REST interface for managing films, categories, rentals, and AI-powered interactions. Built with FastAPI, it offers automatic documentation, type safety, and high performance.

## 🚀 API Features

### Core Capabilities
- **Film Management**: CRUD operations for movies and metadata
- **Category System**: Genre-based film organization
- **Rental Operations**: Rental management and tracking
- **Customer Management**: User account operations
- **AI Integration**: Intelligent film recommendations and Q&A

### Technical Features
- **Automatic Documentation**: Interactive Swagger UI and ReDoc
- **Type Safety**: Pydantic models for validation
- **Async Operations**: High-performance async/await
- **Error Handling**: Consistent error responses
- **Authentication**: JWT-based security (ready)

## 📋 API Structure

### Base URL
```
Development: http://localhost:8000
Production: https://your-domain.com
```

### API Versioning
```
/api/v1/  # Current version
```

### Content Type
```
Content-Type: application/json
Accept: application/json
```

## 🔗 Endpoint Categories

### 1. Health & Status
```
GET  /health              # Application health check
GET  /                    # Root endpoint with API info
```

### 2. Film Operations
```
GET    /api/v1/films/           # List all films
GET    /api/v1/films/{id}       # Get specific film
POST   /api/v1/films/           # Create new film
PUT    /api/v1/films/{id}       # Update film
DELETE /api/v1/films/{id}       # Delete film
GET    /api/v1/films/search     # Search films
```

### 3. Category Management
```
GET    /api/v1/categories/      # List all categories
GET    /api/v1/categories/{id}  # Get specific category
POST   /api/v1/categories/      # Create category
PUT    /api/v1/categories/{id}  # Update category
DELETE /api/v1/categories/{id}  # Delete category
```

### 4. Rental System
```
GET    /api/v1/rentals/         # List rentals
GET    /api/v1/rentals/{id}     # Get rental details
POST   /api/v1/rentals/         # Create rental
PUT    /api/v1/rentals/{id}     # Update rental
DELETE /api/v1/rentals/{id}     # Return/cancel rental
```

### 5. Customer Operations
```
GET    /api/v1/customers/       # List customers
GET    /api/v1/customers/{id}   # Get customer details
POST   /api/v1/customers/       # Create customer
PUT    /api/v1/customers/{id}   # Update customer
DELETE /api/v1/customers/{id}   # Delete customer
```

### 6. AI Services
```
POST   /api/v1/ai/handoff      # AI agent interaction
POST   /api/v1/ai/search       # AI-powered film search
POST   /api/v1/ai/recommend    # Film recommendations
```

## 📊 Response Format

### Success Response
```json
{
  "data": {
    // Response data
  },
  "message": "Success",
  "status_code": 200
}
```

### Error Response
```json
{
  "detail": "Error description",
  "status_code": 400,
  "error_type": "ValidationError"
}
```

### Paginated Response
```json
{
  "items": [
    // Array of items
  ],
  "total": 1000,
  "page": 1,
  "size": 50,
  "pages": 20
}
```

## 🔐 Authentication

### JWT Authentication (Ready)
```http
Authorization: Bearer <jwt_token>
```

### Authentication Flow
```
1. POST /auth/login     # Get JWT token
2. Include token in Authorization header
3. Token expires after configured time
4. Refresh token as needed
```

## 📝 Request/Response Models

### Film Models
```python
# Request Model
class FilmCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    release_year: Optional[int] = Field(None, ge=1900, le=2030)
    rental_duration: int = Field(3, ge=1, le=30)
    rental_rate: float = Field(4.99, ge=0)
    rating: Optional[str] = Field("G", regex="^(G|PG|PG-13|R|NC-17)$")

# Response Model
class FilmResponse(BaseModel):
    film_id: int
    title: str
    description: Optional[str]
    release_year: Optional[int]
    rental_duration: int
    rental_rate: float
    rating: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### AI Models
```python
class HandoffRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    context: Optional[dict] = None

class HandoffResponse(BaseModel):
    answer: str
    agent: str
    confidence: Optional[float] = None
    sources: Optional[List[str]] = None
```

## 🔍 Query Parameters

### Pagination
```
?skip=0&limit=50        # Offset-based pagination
?page=1&size=50         # Page-based pagination
```

### Filtering
```
?category=Action        # Filter by category
?year=2023             # Filter by release year
?rating=PG-13          # Filter by rating
```

### Sorting
```
?sort=title            # Sort by title (ascending)
?sort=-release_year    # Sort by year (descending)
?sort=title,release_year  # Multiple sort fields
```

### Search
```
?q=inception           # General search
?title=inception       # Title search
?description=dream     # Description search
```

## 📈 Rate Limiting

### Default Limits
```
- 100 requests per minute per IP
- 1000 requests per hour per authenticated user
- 10 requests per minute for AI endpoints
```

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 🚨 Error Codes

### HTTP Status Codes
| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Validation Error | Invalid input data |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Error | Server error |

### Custom Error Types
```python
class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class ValidationError(APIError):
    pass

class NotFoundError(APIError):
    def __init__(self, resource: str, id: Any):
        super().__init__(f"{resource} with id {id} not found", 404)

class AuthenticationError(APIError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)
```

## 🔧 API Configuration

### Environment Variables
```bash
# API Configuration
API_V1_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000
DEBUG=False

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
CORS_METHODS=["GET", "POST", "PUT", "DELETE"]

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=100
```

### FastAPI Configuration
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Interview API",
    description="FastAPI with AI agent orchestration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📚 Interactive Documentation

### Swagger UI
```
URL: http://localhost:8000/docs
Features:
- Interactive API testing
- Request/response examples
- Schema documentation
- Authentication testing
```

### ReDoc
```
URL: http://localhost:8000/redoc
Features:
- Clean documentation layout
- Detailed schema information
- Code examples
- Download OpenAPI spec
```

### OpenAPI Specification
```
URL: http://localhost:8000/openapi.json
Format: OpenAPI 3.0.3
Usage: API client generation, testing tools
```

## 🧪 API Testing

### Test Client Setup
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_films():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/films/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
```

### Example Requests
```bash
# Get all films
curl -X GET "http://localhost:8000/api/v1/films/" \
  -H "Accept: application/json"

# Create a film
curl -X POST "http://localhost:8000/api/v1/films/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Film",
    "description": "A great new film",
    "release_year": 2023,
    "rating": "PG-13"
  }'

# AI interaction
curl -X POST "http://localhost:8000/api/v1/ai/handoff" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tell me about action movies from 2010"
  }'
```

## 🔄 API Versioning Strategy

### Current Version: v1
- Stable API with backward compatibility
- All endpoints prefixed with `/api/v1/`
- Semantic versioning for major changes

### Future Versioning
```
/api/v2/  # Future version with breaking changes
/api/v1/  # Maintained for backward compatibility
```

### Version Headers
```http
API-Version: 1.0
Accept-Version: 1.0
```

## 📊 Performance Considerations

### Response Time Targets
- Simple queries: < 100ms
- Complex queries: < 500ms
- AI interactions: < 2000ms
- File uploads: < 5000ms

### Optimization Strategies
- Database query optimization
- Response caching
- Connection pooling
- Async operations
- Pagination for large datasets

This API design provides a robust, scalable, and developer-friendly interface for all application functionality while maintaining high performance and security standards.
