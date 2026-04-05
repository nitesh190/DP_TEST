from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import engine, SessionLocal, Base
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer
from fastapi import Security
from fastapi import Form
from .auth import create_access_token




security = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

fake_user = {
    "username": "admin",
    "password": "admin123"
}



Base.metadata.create_all(bind=engine)

app = FastAPI(title="Doctor Microservice")

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username != fake_user["username"] or password != fake_user["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/basic-secure")
def basic_auth(credentials: HTTPBasicCredentials = Security(security)):
    if credentials.username != fake_user["username"] or credentials.password != fake_user["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Basic Auth Success"}



from jose import jwt, JWTError
from fastapi import Depends

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/secure-data")
def secure_data(user: str = Depends(get_current_user)):
    return {"message": f"Hello {user}, secure data access granted"}



# Create Doctor
@app.post("/doctors", response_model=schemas.DoctorResponse)
def add_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    return crud.create_doctor(db, doctor)

# Get All Doctors
@app.get("/doctors")
def list_doctors(db: Session = Depends(get_db)):
    return crud.get_doctors(db)

# Count Doctors
@app.get("/doctors/count")
def count_doctors(db: Session = Depends(get_db)):
    return {"total_doctors": crud.get_doctor_count(db)}

# Update Doctor
@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    updated = crud.update_doctor(db, doctor_id, doctor)
    if not updated:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return updated

# Delete Doctor
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    if not crud.delete_doctor(db, doctor_id):
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"message": "Deleted successfully"}