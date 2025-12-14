from pydantic import BaseModel, Field
from typing import Optional

# --- 基礎模型 ---
class BookBase(BaseModel):
    title: str
    author: str
    publisher: Optional[str] = None
    # 設定 price 必須大於 0 (gt = greater than)
    price: int = Field(..., gt=0, description="價格必須大於 0")
    publish_date: Optional[str] = None
    isbn: Optional[str] = None
    cover_url: Optional[str] = None

# --- 建立與更新用的模型 ---
# 為了配合資料庫 NOT NULL 的限制，通常 POST (Create) 還是需要必填欄位
# 但我們會加上你要求的 price > 0 驗證
class BookCreate(BookBase):
    pass

# 針對 PUT (Update)，欄位通常是選填的，但如果有填寫 price，一樣要 > 0
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    price: Optional[int] = Field(None, gt=0)
    publish_date: Optional[str] = None
    isbn: Optional[str] = None
    cover_url: Optional[str] = None

# --- 回傳用模型 (BookResponse) ---
# 用於 API 回傳（一定要有 id 與 created_at）
class BookResponse(BookBase):
    id: int
    created_at: Optional[str] = None # 資料庫會自動產生，讀取時會有值