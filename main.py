from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import firebase_admin
from firebase_admin import credentials, firestore

app = FastAPI()

cred = credentials.Certificate("student-library-mngmnt-system-firebase-adminsdk-fbsvc-770b2d23a3.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

class Book(BaseModel):
    id: int
    title: str

class Student(BaseModel):
    id: int
    name: str

class AssignBook(BaseModel):
    book_id: int
    student_id: int

# Add books by post method
@app.post("/books")
def add_book(book: Book):
    book_ref = db.collection("Books").document(str(book.id))
    if book_ref.get().exists:
        raise HTTPException(status_code=400, detail="Book ID already exists")
    
    book_ref.set({"title": book.title})
    return {"message": "Book added successfully"}

# Read all added books by get method
@app.get("/books")
def get_books():
    books = {}
    books_ref = db.collection("Books").stream()
    for doc in books_ref:
        books[int(doc.id)] = doc.to_dict()["title"]
    return books

# Update book data using Put method
@app.put("/books")
def update_book(book: Book):
    book_ref = db.collection("Books").document(str(book.id))
    if not book_ref.get().exists:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book_ref.update({"title": book.title})
    return {"message": "Book updated successfully"}

# Delete book data using Delete method
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book_ref = db.collection("Books").document(str(book_id))
    if not book_ref.get().exists:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book_ref.delete()
    return {"message": "Book deleted successfully"}

# Add student by post method
@app.post("/students")
def add_student(student: Student):
    student_ref = db.collection("Students").document(str(student.id))
    if student_ref.get().exists:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    
    student_ref.set({"name": student.name})
    return {"message": "Student added successfully"}

# Read all added students by get method
@app.get("/students")
def get_students():
    students = {}
    students_ref = db.collection("Students").stream()
    for doc in students_ref:
        students[int(doc.id)] = doc.to_dict()["name"]
    return students

@app.post("/assign")
def assign_book(assignment: AssignBook):
    book_ref = db.collection("Books").document(str(assignment.book_id))
    student_ref = db.collection("Students").document(str(assignment.student_id))

    if not book_ref.get().exists:
        raise HTTPException(status_code=404, detail="Book not found")
    if not student_ref.get().exists:
        raise HTTPException(status_code=404, detail="Student not found")

    assignment_ref = db.collection("Assignments").document(str(assignment.book_id))
    assignment_ref.set({"student_id": assignment.student_id})

    return {"message": "Book assigned successfully"}

@app.get("/assignments")
def get_assignments():
    assignments = {}
    assignments_ref = db.collection("Assignments").stream()
    
    for doc in assignments_ref:
        book_id = int(doc.id)
        student_id = doc.to_dict()["student_id"]

        # Get book title
        book_ref = db.collection("Books").document(str(book_id)).get()
        book_title = book_ref.to_dict()["title"] if book_ref.exists else "Unknown Book"

        student_ref = db.collection("Students").document(str(student_id)).get()
        student_name = student_ref.to_dict()["name"] if student_ref.exists else "Unknown"

        assignments[book_title] = student_name

    return assignments
