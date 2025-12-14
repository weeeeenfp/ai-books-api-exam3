from fastapi import FastAPI, HTTPException, Query, Path, status
from typing import List

# 匯入我們之前寫好的模組
import database as db
from models import BookCreate, BookUpdate, BookResponse

# 設定 API 的標題
app = FastAPI(title="AI Books API")


# 1. 根目錄 (Root)
@app.get("/", status_code=status.HTTP_200_OK)
def read_root() -> dict:
    """
    根目錄端點。
    回傳歡迎訊息。
    """
    return {"message": "AI Books API"}


# 2. 取得所有書籍 (分頁)
@app.get("/books", response_model=List[BookResponse], status_code=status.HTTP_200_OK)
def read_books(
        skip: int = Query(0, ge=0, description="跳過前 N 筆資料"),
        limit: int = Query(10, gt=0, le=100, description="一次取得 N 筆資料")
) -> List[dict]:
    """
    分頁取得書籍列表。
    - skip: 從第幾筆開始 (預設 0)
    - limit: 一次顯示幾筆 (預設 10)
    """
    books = db.get_all_books(skip=skip, limit=limit)
    return books


# 3. 取得單一書籍
@app.get("/books/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def read_book(book_id: int = Path(..., description="書籍 ID")) -> dict:
    """
    根據 ID 取得單一書籍詳細資料。
    若找不到書籍，回傳 404 錯誤。
    """
    book = db.get_book_by_id(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# 4. 新增一本書
@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def add_book(book: BookCreate) -> dict:
    """
    新增一本新書。
    成功後回傳 201 Created 與該書籍的完整資料。
    """
    # 呼叫資料庫函式新增資料，取得新 ID
    new_id = db.create_book(
        title=book.title,
        author=book.author,
        publisher=book.publisher,
        price=book.price,
        publish_date=book.publish_date,
        isbn=book.isbn,
        cover_url=book.cover_url
    )

    # 為了回傳完整的 BookResponse (包含 created_at)，我們用新 ID 再查一次
    new_book = db.get_book_by_id(new_id)
    return new_book


# 5. 完整更新一本書
@app.put("/books/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def update_book_info(
        book_id: int,
        book_update: BookUpdate
) -> dict:
    """
    完整更新書籍資料。
    若欄位未提供，則維持原資料庫內的數值。
    若找不到書籍，回傳 404 錯誤。
    """
    # 1. 先檢查書籍是否存在
    existing_book = db.get_book_by_id(book_id)
    if existing_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    # 2. 準備更新資料
    # 邏輯：如果使用者在 JSON 中沒傳某個欄位 (None)，就使用資料庫原本的舊值
    updated_title = book_update.title if book_update.title is not None else existing_book["title"]
    updated_author = book_update.author if book_update.author is not None else existing_book["author"]
    updated_publisher = book_update.publisher if book_update.publisher is not None else existing_book["publisher"]
    updated_price = book_update.price if book_update.price is not None else existing_book["price"]
    updated_publish_date = book_update.publish_date if book_update.publish_date is not None else existing_book[
        "publish_date"]
    updated_isbn = book_update.isbn if book_update.isbn is not None else existing_book["isbn"]
    updated_cover_url = book_update.cover_url if book_update.cover_url is not None else existing_book["cover_url"]

    # 3. 執行更新
    success = db.update_book(
        book_id=book_id,
        title=updated_title,
        author=updated_author,
        publisher=updated_publisher,
        price=updated_price,
        publish_date=updated_publish_date,
        isbn=updated_isbn,
        cover_url=updated_cover_url
    )

    # 理論上前面檢查過 existing_book，這裡不太會失敗，但以防萬一
    if not success:
        raise HTTPException(status_code=404, detail="Book not found during update")

    # 4. 回傳更新後的完整資料
    return db.get_book_by_id(book_id)


# 6. 刪除一本書
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_info(book_id: int):
    """
    刪除指定書籍。
    成功刪除回傳 204 No Content (不回傳任何 body)。
    若找不到書籍，回傳 404 錯誤。
    """
    success = db.delete_book(book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")

    # 204 回傳不用 return 任何東西，FastAPI 會自動處理
    return