# backend.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date
import uvicorn
import threading

# --- Database Setup (SQLite) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./hrms.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Models ---
class EmployeeDB(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    emp_id_str = Column(String, unique=True, index=True) # e.g. "EMP001"
    name = Column(String)
    email = Column(String, unique=True)
    department = Column(String)

class AttendanceDB(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    emp_id_str = Column(String) # Foreign Key reference
    date = Column(Date)
    status = Column(String) # "Present" or "Absent"

Base.metadata.create_all(bind=engine)

# --- Pydantic Schemas (Data Validation) ---
class EmployeeSchema(BaseModel):
    emp_id_str: str
    name: str
    email: str
    department: str

class AttendanceSchema(BaseModel):
    emp_id_str: str
    date: date
    status: str

# --- API App ---
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Add Employee
@app.post("/employees/")
def add_employee(emp: EmployeeSchema):
    db = SessionLocal()
    # Check duplicate
    if db.query(EmployeeDB).filter(EmployeeDB.emp_id_str == emp.emp_id_str).first():
        db.close()
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    new_emp = EmployeeDB(**emp.dict())
    db.add(new_emp)
    db.commit()
    db.close()
    return {"message": "Employee added successfully"}

# 2. Get All Employees
@app.get("/employees/")
def get_employees():
    db = SessionLocal()
    emps = db.query(EmployeeDB).all()
    db.close()
    return emps

# 3. Delete Employee
@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: str):
    db = SessionLocal()
    emp = db.query(EmployeeDB).filter(EmployeeDB.emp_id_str == emp_id).first()
    if not emp:
        db.close()
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()
    db.close()
    return {"message": "Deleted"}

# 4. Mark Attendance
@app.post("/attendance/")
def mark_attendance(att: AttendanceSchema):
    db = SessionLocal()
    # Check if employee exists
    if not db.query(EmployeeDB).filter(EmployeeDB.emp_id_str == att.emp_id_str).first():
        db.close()
        raise HTTPException(status_code=404, detail="Employee ID not found")
    
    new_att = AttendanceDB(**att.dict())
    db.add(new_att)
    db.commit()
    db.close()
    return {"message": "Attendance Marked"}

# 5. Get Attendance
@app.get("/attendance/{emp_id}")
def get_attendance(emp_id: str):
    db = SessionLocal()
    records = db.query(AttendanceDB).filter(AttendanceDB.emp_id_str == emp_id).all()
    db.close()
    return records

# Code to run this in VS Code directly (Optional for deployment, good for local)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)