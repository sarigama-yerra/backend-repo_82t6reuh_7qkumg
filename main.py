import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from database import db, create_document, get_documents
from schemas import User, Competition, LostItem, Event as EventSchema, ForumPost, Comment
import hashlib
from bson.objectid import ObjectId

app = FastAPI(title="Younifirst API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class CreateCompetition(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    deadline: Optional[str] = None
    link: Optional[str] = None

class CreateLostItem(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = "lost"
    contact: Optional[str] = None

class CreateEvent(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    link: Optional[str] = None

class CreateForumPost(BaseModel):
    title: str
    content: str
    author: Optional[str] = None
    tags: Optional[List[str]] = None

class CreateComment(BaseModel):
    post_id: str
    content: str
    author: Optional[str] = None

@app.get("/")
def root():
    return {"message": "Younifirst API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

# Utility

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Auth endpoints (simple email/password with hashed storage)

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

@app.post("/auth/register")
def register_user(payload: RegisterRequest):
    # check if user exists
    existing = db["user"].find_one({"email": payload.email}) if db else None
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_model = User(name=payload.name, email=payload.email, password_hash=hash_password(payload.password))
    user_id = create_document("user", user_model)
    return {"id": user_id, "email": payload.email, "name": payload.name}

@app.post("/auth/login")
def login(payload: LoginRequest):
    user = db["user"].find_one({"email": payload.email}) if db else None
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.get("password_hash") != hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user": {"id": str(user.get("_id")), "name": user.get("name"), "email": user.get("email")}}

# Dashboard: simple summary counts
@app.get("/dashboard/summary")
def dashboard_summary():
    def count(col):
        return db[col].count_documents({}) if db else 0
    return {
        "users": count("user"),
        "competitions": count("competition"),
        "lost_items": count("lostitem"),
        "events": count("event"),
        "posts": count("forumpost"),
    }

# Competitions
@app.get("/competitions")
def list_competitions():
    items = get_documents("competition") if db else []
    for it in items:
        it["id"] = str(it.pop("_id"))
    return items

@app.post("/competitions")
def create_competition(payload: CreateCompetition):
    comp = Competition(**payload.model_dump())
    _id = create_document("competition", comp)
    return {"id": _id}

# Lost & Found
@app.get("/lostfound")
def list_lostfound():
    items = get_documents("lostitem") if db else []
    for it in items:
        it["id"] = str(it.pop("_id"))
    return items

@app.post("/lostfound")
def create_lostfound(payload: CreateLostItem):
    item = LostItem(**payload.model_dump())
    _id = create_document("lostitem", item)
    return {"id": _id}

# Events
@app.get("/events")
def list_events():
    items = get_documents("event") if db else []
    for it in items:
        it["id"] = str(it.pop("_id"))
    return items

@app.post("/events")
def create_event(payload: CreateEvent):
    ev = EventSchema(**payload.model_dump())
    _id = create_document("event", ev)
    return {"id": _id}

# Forum
@app.get("/forum/posts")
def list_posts():
    items = get_documents("forumpost") if db else []
    for it in items:
        it["id"] = str(it.pop("_id"))
    return items

@app.post("/forum/posts")
def create_post(payload: CreateForumPost):
    p = ForumPost(**payload.model_dump())
    _id = create_document("forumpost", p)
    return {"id": _id}

@app.get("/forum/posts/{post_id}/comments")
def list_comments(post_id: str):
    filter_dict = {"post_id": post_id}
    items = get_documents("comment", filter_dict=filter_dict) if db else []
    for it in items:
        it["id"] = str(it.pop("_id"))
    return items

@app.post("/forum/comments")
def create_comment(payload: CreateComment):
    c = Comment(**payload.model_dump())
    _id = create_document("comment", c)
    return {"id": _id}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
