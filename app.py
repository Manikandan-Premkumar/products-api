import base64

from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row

from database import get_connection, initialize_db

app = FastAPI()


@app.on_event("startup")
def startup_event():
    initialize_db()


def encode_cursor(created_at, product_id):
    cursor = f"{created_at.isoformat()}|{product_id}"
    return base64.b64encode(cursor.encode()).decode()


def decode_cursor(page_cursor):
    decoded = base64.b64decode(page_cursor).decode()
    created_at, product_id = decoded.split("|")
    return created_at, int(product_id)


@app.get("/products")
def get_products(
    limit: int = 20,
    category: str = None,
    page_cursor: str = None
):

    try:
        conn = get_connection()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

    db_cursor = conn.cursor(row_factory=dict_row)

    created_at = None
    product_id = None

    if page_cursor:
        created_at, product_id = decode_cursor(page_cursor)

    
    if category and page_cursor:

        db_cursor.execute(
            """
            SELECT
                id,
                name,
                category,
                price,
                created_at,
                updated_at
            FROM products
            WHERE category = %s
              AND (created_at, id) < (%s, %s)
            ORDER BY created_at DESC, id DESC
            LIMIT %s
            """,
            (category, created_at, product_id, limit)
        )

    elif category:

        db_cursor.execute(
            """
            SELECT
                id,
                name,
                category,
                price,
                created_at,
                updated_at
            FROM products
            WHERE category = %s
            ORDER BY created_at DESC, id DESC
            LIMIT %s
            """,
            (category, limit)
        )

    
    elif page_cursor:

        db_cursor.execute(
            """
            SELECT
                id,
                name,
                category,
                price,
                created_at,
                updated_at
            FROM products
            WHERE (created_at, id) < (%s, %s)
            ORDER BY created_at DESC, id DESC
            LIMIT %s
            """,
            (created_at, product_id, limit)
        )

    
    else:

        db_cursor.execute(
            """
            SELECT
                id,
                name,
                category,
                price,
                created_at,
                updated_at
            FROM products
            ORDER BY created_at DESC, id DESC
            LIMIT %s
            """,
            (limit,)
        )

    products = db_cursor.fetchall()

    next_cursor = None

    if products:
        last = products[-1]

        next_cursor = encode_cursor(
            last["created_at"],
            last["id"]
        )

    db_cursor.close()
    conn.close()

    return {
        "items": products,
        "next_cursor": next_cursor
    }