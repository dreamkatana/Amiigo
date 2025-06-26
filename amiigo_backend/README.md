# Amiigo Backend

This is the backend for the Amiigo dating application, built with FastAPI and PostgreSQL.

## Setup

1.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Set up your PostgreSQL database and configure the connection string in a `.env` file (see `.env.example` when available).

4.  Run database migrations (if using Alembic):
    ```bash
    alembic upgrade head
    ```

5.  Run the development server:
    ```bash
    uvicorn app.main:app --reload
    ```

The API will be available at `http://127.0.0.1:8000`.

## Project Structure

(Details to be added as the project develops)
```
