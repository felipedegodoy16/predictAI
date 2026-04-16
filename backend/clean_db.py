import sqlite3

def clean_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM django_migrations WHERE app='work_orders'")
        cursor.execute("DROP TABLE IF EXISTS work_orders_workorder")
        print("Limpeza concluída com sucesso.")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        conn.commit()
        conn.close()

if __name__ == '__main__':
    clean_db()
