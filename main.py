from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
import models
from database import Base, engine, get_db

# Create DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

# ---------------- Pydantic Schemas ----------------

class BookCreate(BaseModel):
    title: str
    author: str
    first_publish_year: Optional[int] = None

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    first_publish_year: Optional[int] = None

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    first_publish_year: Optional[int]

    class Config:
        from_attributes = True  # Required for SQLAlchemy integration in Pydantic v2

# ---------------- Routes ----------------

@app.post("/books/", response_model=BookOut)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@app.patch("/books/{book_id}", response_model=BookOut)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    for key, value in book.model_dump(exclude_unset=True).items():
        setattr(db_book, key, value)

    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete("/books/{book_id}", response_model=Dict[str, Any])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted"}
