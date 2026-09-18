# Lumen

Lumen is a personal finance dashboard for recording the money coming in and going out, then turning that ledger into an easy-to-read view of your financial habits.

Each person creates a private account and manages only their own transactions. Lumen stores the data in PostgreSQL and presents it through three focused views:

- **Overview** shows total balance, recorded income and spending, a daily spending average, recent activity, and expense totals by category.
- **Activity** is the complete transaction ledger, where entries can be reviewed and edited.
- **Planning** uses recorded income and expenses to show category patterns, suggest a flexible-spending starting point (30% of income), and offer a configurable 20% savings prompt.

## What you can do

- Register, sign in, and sign out securely. Passwords are stored as hashes, not plain text.
- Add income or expense transactions with a description, amount, category, and date.
- Keep transactions private to the signed-in account.
- Edit an existing transaction from the Activity page.
- See totals and spending categories update from the transactions you record.
- Switch between light and dark themes.

Lumen accepts only positive transaction amounts and prevents dates in the future. Dashboard totals reflect all transactions currently recorded for the signed-in user.

## Run locally

1. Create a PostgreSQL database (for example, `ledgerly`).
2. Copy `.env.example` to `.env` and set a secure `SECRET_KEY` plus the connection string for your database.
3. Install dependencies and start the development server:

   ```powershell
   python -m pip install -r requirements.txt
   python app.py
   ```

4. Open `http://127.0.0.1:5000`, create an account, and add your first transaction.

The app creates the `user` and `transaction` tables automatically on startup. Alternatively, after configuring the environment, run `flask --app app init-db` to create them explicitly.

## Configuration

```env
SECRET_KEY=a-long-random-secret
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ledgerly
```

`SECRET_KEY` protects login sessions. Use a long, unique random value outside local development. `DATABASE_URL` must point to an accessible PostgreSQL database.

## Stack

- Flask with Flask-Login for authentication
- Flask-SQLAlchemy and PostgreSQL for persistence
- Server-rendered HTML, CSS, and a small JavaScript theme toggle
