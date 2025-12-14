import sqlite3

DB_NAME = "bokelai.db"

def get_db_connection() -> sqlite3.Connection:
    """
    建立與 SQLite 資料庫的連線，並設定 row_factory。
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 讓結果像字典一樣存取
    return conn

def get_all_books(skip: int, limit: int) -> list[dict]:
    """
    取得所有書籍資料，支援分頁 (skip, limit)。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM books LIMIT ? OFFSET ?', (limit, skip))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        cursor.close()
        conn.close()

def get_book_by_id(book_id: int) -> dict | None:
    """
    根據 ID 取得單一書籍資料。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        cursor.close()
        conn.close()

def create_book(title: str, author: str, publisher: str | None, price: int, publish_date: str | None, isbn: str | None, cover_url: str | None) -> int:
    """
    新增書籍，並回傳新產生書籍的 ID。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO books (title, author, publisher, price, publish_date, isbn, cover_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (title, author, publisher, price, publish_date, isbn, cover_url))
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()  # 發生錯誤時復原
        raise
    finally:
        cursor.close()
        conn.close()

def update_book(book_id: int, title: str, author: str, publisher: str | None, price: int, publish_date: str | None, isbn: str | None, cover_url: str | None) -> bool:
    """
    更新書籍資料。如果更新成功回傳 True，否則 False。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        UPDATE books 
        SET title = ?, author = ?, publisher = ?, price = ?, publish_date = ?, isbn = ?, cover_url = ?
        WHERE id = ?
        """
        cursor.execute(sql, (title, author, publisher, price, publish_date, isbn, cover_url, book_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def delete_book(book_id: int) -> bool:
    """
    刪除書籍。如果刪除成功回傳 True，否則 False。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()