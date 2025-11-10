# Database Constraint Validation Fixes

## Issue Summary

The application was encountering database constraint violations with the error:
```
asyncpg.exceptions.CheckViolationError: value for domain year violates check constraint "year_check"
```

This error occurred when trying to create or update films with invalid `release_year` values that violated the database's year domain constraint.

## Root Cause

The Pagila database schema defines a `year` domain with a check constraint:

```sql
CREATE DOMAIN public.year AS integer
    CONSTRAINT year_check CHECK (((VALUE >= 1901) AND (VALUE <= 2155)));
```

The application's Pydantic models lacked validation to ensure data conformed to this constraint before attempting database operations, leading to runtime errors instead of user-friendly validation messages.

## Solution Implemented

### 1. Added Pydantic Field Validators

**File: `domain/models/film.py`**
- Added `@field_validator('release_year')` to validate years are between 1901-2155
- Added validators for other fields to ensure data integrity:
  - `rental_duration`: Must be positive
  - `rental_rate` and `replacement_cost`: Must be positive
  - `length`: Must be positive (if provided)

**File: `domain/schemas/film.py`**
- Added identical validators to `FilmUpdate` schema for update operations
- Ensures validation applies to both create and update operations

### 2. Enhanced Error Handling

**File: `api/v1/film_routes.py`**
- Added comprehensive error handling in `create_film()` and `update_film()` endpoints
- Catches `ValidationError` and `IntegrityError` exceptions
- Returns user-friendly HTTP 400 responses with clear error messages
- Specific handling for year constraint violations

### 3. Comprehensive Test Coverage

**File: `tests/test_films.py`**
- Added 8 new validation test cases covering:
  - Year validation (too low, too high, boundary values)
  - Negative value validation (rental_duration, rental_rate, length)
  - Update operation validation
  - Boundary condition testing (1901 and 2155)

## Validation Rules Implemented

### Release Year
- **Range**: 1901 to 2155 (inclusive)
- **Error Message**: "Release year must be between 1901 and 2155 (inclusive). Got: {value}"

### Rental Duration
- **Rule**: Must be positive integer
- **Error Message**: "Rental duration must be positive. Got: {value}"

### Monetary Amounts (rental_rate, replacement_cost)
- **Rule**: Must be positive float
- **Error Message**: "Amount must be positive. Got: {value}"

### Film Length
- **Rule**: Must be positive integer (if provided)
- **Error Message**: "Film length must be positive. Got: {value}"

## API Error Responses

### Validation Errors (HTTP 422)
Pydantic validation errors return structured error responses:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "release_year"],
      "msg": "Release year must be between 1901 and 2155 (inclusive). Got: 1800",
      "input": 1800
    }
  ]
}
```

### Database Constraint Errors (HTTP 400)
If validation is bypassed and database constraints are violated:
```json
{
  "detail": "Release year must be between 1901 and 2155 (inclusive)"
}
```

## Testing

All validation scenarios are covered by automated tests:

```bash
# Run year validation tests
pytest tests/test_films.py -k "invalid" -v

# Run negative value validation tests  
pytest tests/test_films.py -k "negative" -v

# Run boundary condition tests
pytest tests/test_films.py::test_create_film_valid_year_boundaries -v
```

## Benefits

1. **Prevents Runtime Errors**: Validation occurs at the API boundary before database operations
2. **User-Friendly Messages**: Clear, actionable error messages instead of cryptic database errors
3. **Consistent Validation**: Same rules apply to both create and update operations
4. **Comprehensive Coverage**: All numeric fields validated for business logic compliance
5. **Maintainable**: Centralized validation logic in Pydantic models
6. **Testable**: Full test coverage ensures validation works correctly

## Future Considerations

- Consider adding validation for other database constraints as they're discovered
- Monitor for additional constraint violations in production logs
- Add validation for foreign key relationships if needed
- Consider adding custom validation decorators for reusable constraint patterns
