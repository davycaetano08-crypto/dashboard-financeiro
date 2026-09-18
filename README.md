# Lumen financial dashboard

A Flask financial dashboard with account registration, secure login, per-user transactions, and PostgreSQL storage.

## Run it

1. Create a PostgreSQL database named `ledgerly`.
2. Copy `.env.example` to `.env` and set `SECRET_KEY` and `DATABASE_URL` for your database.
3. Install dependencies and start the server:

   ```powershell
   python -m pip install -r requirements.txt
   python app.py
   ```

4. Visit `http://127.0.0.1:5000`, create an account, and add transactions.

The app creates the `user` and `transaction` tables automatically on startup. Alternatively, use `flask --app app init-db` after setting the environment variables.

## Environment

```env
SECRET_KEY=a-long-random-secret
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ledgerly
```
