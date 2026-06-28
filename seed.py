import random
from datetime import datetime, timedelta

from faker import Faker
import psycopg

fake = Faker()

conn = psycopg.connect(
    host="localhost",
    port=5433,
    dbname="products",
    user="postgres",
    password="postgres123"
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