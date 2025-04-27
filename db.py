import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Create a connection
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# insert function
def insert_game(game, price, release_date, thumbnail, description):
    try:
        cursor.execute("""
            INSERT INTO scraped_games (game, price, release_date, thumbnail, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (game, price, release_date, thumbnail, description))
        conn.commit()
        print('Game added to database.')
    except Exception as e:
        print("Error inserting into database:", e)
        conn.rollback()


def close_db():
    cursor.close()
    conn.close()