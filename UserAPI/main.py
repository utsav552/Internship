from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session, relationship
from typing import List
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from database import engine, Base, SessionLocal

class UserDepartment(Base):
    __tablename__ = "user_departments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    is_active = Column(Boolean, default=True)

    departments = relationship(
        "Department",
        secondary="user_departments",
        backref="users"
    )


class DepartmentSchema(BaseModel):
    id: int | None = None
    name: str

    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    email: str
    is_active: bool = True
    departments: List[str] = []    

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/user")
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    new_user = User(
        email=user.email,
        is_active=user.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    for dept_name in user.departments:
        dept = db.query(Department).filter(Department.name == dept_name).first()
        if not dept:
            dept = Department(name=dept_name)
            db.add(dept)
            db.commit()
            db.refresh(dept)

        link = UserDepartment(user_id=new_user.id, department_id=dept.id)
        db.add(link)

    db.commit()

    return {
        "id": new_user.id,
        "email": new_user.email,
        "is_active": new_user.is_active,
        "departments": user.departments
    }
