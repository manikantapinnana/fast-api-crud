# Python FastAPI JWT Auth Example

This project is a small FastAPI application with user registration, JWT login, and protected user routes.

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Environment

Set the following environment variables in production:

- `SECRET_KEY` - strong random secret used to sign JWTs
- `ACCESS_TOKEN_EXPIRE_MINUTES` - token expiry in minutes

The app uses defaults for development when environment variables are not set.

## Run

Start the app with:

```bash
uvicorn main:app --reload
```

Then open:

- `http://127.0.0.1:8000/docs` for Swagger UI
- `http://127.0.0.1:8000/redoc` for ReDoc

## API Endpoints

### Auth endpoints

- `POST /auth/register`
  - Request body: `first_name`, `last_name`, `email`, `password`
  - Returns registered user data (password is never returned)

- `POST /auth/login`
  - Accepts OAuth2 form data with fields `username` and `password`
  - Use `username` as the email value
  - Returns `access_token` and `token_type`

### Protected user endpoints

- `GET /users/me`
  - Requires `Authorization: Bearer <token>`
  - Returns the currently authenticated user

- `GET /users/`
  - Returns all users

- `GET /users/{user_id}`
  - Returns the user by ID

- `PUT /users/update`
  - Updates user data

- `DELETE /users/{user_id}`
  - Deletes a user

## Notes

- Passwords are hashed using Argon2 and `passlib`
- JWTs are signed with `python-jose`
- The Swagger Authorize button uses `/auth/login` as the token endpoint
- Use `Content-Type: application/x-www-form-urlencoded` when calling `/auth/login` outside Swagger
