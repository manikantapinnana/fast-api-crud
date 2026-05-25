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

## WebSocket Chat

This project includes a realtime chat over WebSocket for users who have an *accepted* chat request between them.

- Endpoint: `ws://<host>/chats/ws/{request_id}`
- Authentication: pass the JWT as a query parameter named `token`, e.g. `?token=<JWT>`
- Message format (send JSON):

```json
{ "content": "Hello there" }
```

- Broadcast behaviour: messages are persisted to the `messages` table and broadcast to other participants connected to the same `request_id` room. The sender will not receive the same broadcast back.

- History: `GET /chats/requests/{request_id}/messages` returns persisted messages for accepted chat requests (requires `Authorization: Bearer <token>` header).

### Important runtime notes

- Ensure a WebSocket-capable server is installed (uvicorn with extras). In your virtualenv run:

```bash
pip install "uvicorn[standard]"
```

- The `/chats` router previously had a global dependency that applied `get_current_user` to all routes. WebSocket routes cannot use `OAuth2PasswordBearer` dependencies directly — the code now authenticates websocket clients manually using the `token` query parameter.

### Manual testing quick guide

1. Start the server:

```bash
uvicorn app.app:app --reload
```

2. Create two users and obtain JWTs via `/auth/login`.
3. User A sends a chat request to user B: `POST /chats/send_request?receiver_id=<B_id>`
4. User B accepts the request: `PUT /chats/requests/{request_id}/status?new_status=accepted` (authenticated)
5. Connect clients to the websocket using each user's JWT:

Browser console example:

```js
const token = '<JWT_FOR_USER_A>'
const ws = new WebSocket(`ws://localhost:8000/chats/ws/${requestId}?token=${token}`)
ws.onmessage = e => console.log('recv', e.data)
ws.onopen = () => ws.send(JSON.stringify({ content: 'hello' }))
```

6. Verify the other participant receives the message and that `GET /chats/requests/{request_id}/messages` includes the message.

If you want, I can add an automated pytest integration example that uses `TestClient.websocket_connect` to simulate multiple clients and verify persistence and broadcasts.
