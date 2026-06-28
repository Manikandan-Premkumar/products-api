import psycopg

def get_connection():
    return psycopg.connect(
        host="localhost",
        port=5433,
        dbname="products",
        user="postgres",
        password="postgres123"
    )

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
""")

conn.commit()

cursor.close()
conn.close()

print("Products table created")