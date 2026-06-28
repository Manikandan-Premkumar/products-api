import os
import random
from datetime import datetime, timedelta

from faker import Faker
from dotenv import load_dotenv
import psycopg

load_dotenv()

fake = Faker()

# Use DATABASE_URL if available, otherwise fall back to individual env vars
database_url = os.getenv("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    conn = psycopg.connect(database_url)
else:
    conn = psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5433")),
        dbname=os.getenv("DB_NAME", "products"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres123"),
        sslmode=os.getenv("DB_SSLMODE", "require"),
    )

cursor = conn.cursor()

categories = [
    "Electronics",
    "Books",
    "Sports",
    "Fashion",
    "Home"
]

TOTAL = 200000
BATCH_SIZE = 1000

for start in range(0, TOTAL, BATCH_SIZE):

    products = []

    for _ in range(BATCH_SIZE):

        created = datetime.now() - timedelta(
            days=random.randint(0,365)
        )

        products.append(
            (
                fake.word().title(),
                random.choice(categories),
                round(random.uniform(100,5000),2),
                created,
                created
            )
        )

    cursor.executemany(
        """
        INSERT INTO products
        (name, category, price, created_at, updated_at)
        VALUES (%s,%s,%s,%s,%s)
        """,
        products
    )

    conn.commit()

    print(f"Inserted {start+BATCH_SIZE}")

cursor.close()
conn.close()

print("Finished")

