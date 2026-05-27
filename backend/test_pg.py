import psycopg2
import sys
import os

try:
    os.environ['LC_ALL'] = 'C'
    conn = psycopg2.connect(
        dbname='predictai',
        user='postgres',
        password='postgres',
        host='localhost',
        port=5432
    )
    print("Success")
except Exception as e:
    print(repr(e))
