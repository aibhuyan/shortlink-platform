import secrets
import string
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Link
from schemas import LinkCreate, LinkRead

CODE_ALPHABET = string.ascii_letters + string.digits


def generate_code(length: int = 6) -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(length))


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from the shortlink API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/links", response_model=LinkRead, status_code=201)
async def create_link(payload: LinkCreate, db: AsyncSession = Depends(get_db)):
    link = Link(code=generate_code(), target_url=payload.target_url)
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link