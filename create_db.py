import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    connection = psycopg2.connect(user="postgres", password="postgres", host="localhost", port="5432")
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE predictai;")
    print("Database created successfully")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection:
        cursor.close()
        connection.close()
