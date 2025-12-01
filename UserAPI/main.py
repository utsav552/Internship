from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, relationship
from typing import List
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
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


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    departments: List[str]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.post("/user", response_model=UserResponse)
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    new_user = User(email=user.email, is_active=user.is_active)
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

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        is_active=new_user.is_active,
        departments=user.departments
    )

@app.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []

    for u in users:
        dept_list = [d.name for d in u.departments]
        result.append(
            UserResponse(
                id=u.id,
                email=u.email,
                is_active=u.is_active,
                departments=dept_list
            )
        )
    return result

@app.get("/user/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    departments = [d.name for d in user.departments]

    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        departments=departments
    )

@app.put("/user/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updated_data: UserSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email = updated_data.email
    user.is_active = updated_data.is_active

    db.query(UserDepartment).filter(UserDepartment.user_id == user.id).delete()

    for dept_name in updated_data.departments:
        dept = db.query(Department).filter(Department.name == dept_name).first()
        if not dept:
            dept = Department(name=dept_name)
            db.add(dept)
            db.commit()
            db.refresh(dept)

        link = UserDepartment(user_id=user.id, department_id=dept.id)
        db.add(link)

    db.commit()

    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        departments=updated_data.departments
    )

@app.delete("/user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(UserDepartment).filter(UserDepartment.user_id == user_id).delete()

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
