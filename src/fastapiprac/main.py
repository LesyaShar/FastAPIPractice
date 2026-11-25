import json
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="FastAPIPractice", description="API для работы с книгами")

# Book — книга. Модель задаёт поля и проверяет типы входных данных.
class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int
    genre: str
    price: float
    in_stock: bool


# Берём data.json из папки с этим скриптом, независимо от места запуска.
FILE = Path(__file__).with_name("data.json")
with open(FILE, encoding="utf-8") as file:
    data = json.load(file)


def save():
    # save — сохранить: записываем изменения обратно в JSON.
    with open(FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


@app.get("/books", response_model=list[Book])
def get_books():
    # GET — получить. Возвращаем список всех книг.
    return data["books"]


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    # Ищем книгу по ID. Если её нет, отвечаем ошибкой 404.
    for book in data["books"]:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Книга не найдена")


@app.post("/books", response_model=Book, status_code=201)
def add_book(book: Book):
    # POST — добавить. Одинаковых ID быть не должно.
    for item in data["books"]:
        if item["id"] == book.id:
            raise HTTPException(status_code=409, detail="Такой ID уже существует")
    new_book = book.model_dump()  # Превращаем модель в обычный словарь.
    data["books"].append(new_book)
    save()
    return new_book


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    # DELETE — удалить. Используем поиск из get_book.
    book = get_book(book_id)
    data["books"].remove(book)
    save()
    return {"message": "Книга удалена"}


@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book: Book):
    # PUT — заменить данные книги целиком. Её ID оставляем прежним.
    old_book = get_book(book_id)
    if book.id != book_id:
        raise HTTPException(status_code=400, detail="ID в адресе и в данных должны совпадать")
    index = data["books"].index(old_book)
    data["books"][index] = book.model_dump()
    save()
    return data["books"][index]


if __name__ == "__main__":
    # Запускаем веб-сервер. Документация: http://localhost:8000/docs
    uvicorn.run(app, host="0.0.0.0", port=8000)
