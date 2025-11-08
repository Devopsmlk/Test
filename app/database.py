import psycopg2
import os
from psycopg2.extras import RealDictCursor

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'qashqade'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        port=os.getenv('DB_PORT', '5432')
    )
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS word_transformations (
            id SERIAL PRIMARY KEY,
            original_word VARCHAR(255) NOT NULL,
            mirrored_word VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

def save_word_pair(original, mirrored):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        'INSERT INTO word_transformations (original_word, mirrored_word) VALUES (%s, %s)',
        (original, mirrored)
    )
    
    conn.commit()
    cur.close()
    conn.close()