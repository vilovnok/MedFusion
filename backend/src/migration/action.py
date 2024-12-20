######
# Action for the main.py
######

drop_tables_sql = [
    "DROP TABLE IF EXISTS messages CASCADE;",
    "DROP TABLE IF EXISTS users CASCADE;",
]

create_tables_sql = [
    """
    CREATE TABLE IF NOT EXISTS "users" (
        id SERIAL PRIMARY KEY,
        username VARCHAR NOT NULL UNIQUE,
        email VARCHAR NOT NULL UNIQUE,
        hashed_password VARCHAR NOT NULL,
        token VARCHAR NOT NULL DEFAULT '',
        created_at TIMESTAMPTZ DEFAULT TIMEZONE('Europe/Moscow', CURRENT_TIMESTAMP)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS "messages" (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        ai_text VARCHAR NOT NULL,
        human_text VARCHAR NOT NULL,
        created_at TIMESTAMPTZ DEFAULT TIMEZONE('Europe/Moscow', CURRENT_TIMESTAMP)
    );
    """
]