from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import firebase_admin
from firebase_admin import credentials, firestore

app = FastAPI()

cred = credentials.Certificate("student-library-mngmnt-system-firebase-adminsdk-fbsvc-770b2d23a3.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# In-memory storage
books: Dict[int, str] = {}  # {book_id: book_title}
students: Dict[int, str] = {}  # {student_id: student_name}
book_assignments: Dict[int, int] = {}  # {book_id: student_id}

class Book(BaseModel):
    id: int
    title: str

class Student(BaseModel):
    id: int
    name: str

class AssignBook(BaseModel):
    book_id: int
    student_id: int

@app.post("/books")
def add_book(book: Book):
    if book.id in books:
        raise HTTPException(status_code=400, detail="Book ID already exists")
    books[book.id] = book.title
    return {"message": "Book added successfully"}

@app.get("/books", response_model=Dict[int, str])
def get_books():
    return books

@app.put("/books")
def update_book(book: Book):
    if book.id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    books[book.id] = book.title
    return {"message": "Book updated successfully"}

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    del books[book_id]
    return {"message": "Book deleted successfully"}

@app.post("/students")
def add_student(student: Student):
    if student.id in students:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    students[student.id] = student.name
    return {"message": "Student added successfully"}


@app.post("/assign")
def assign_book(assignment: AssignBook):
    if assignment.book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    if assignment.student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    book_assignments[assignment.book_id] = assignment.student_id
    return {"message": "Book assigned successfully"}

@app.get("/assignments", response_model=Dict[int, str])
def get_assignments():
    return {book_id: students[student_id] for book_id, student_id in book_assignments.items()}
