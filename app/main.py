from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import user

app = FastAPI(
    title="Event Management APP",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    description="We take care of your events while you are happy and stress free",
    openapi_url="/api/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]  # allows only specified origins above
    ,allow_credentials=True,
    allow_methods=["*"],  # allows all methods
    allow_headers=["*"],  # allows all headers
)


# Include database
Base.metadata.create_all(bind=engine)

app.include_router(user.router, prefix="/api")


# The root of the app. That is the landing/home page.
@app.get("/")
async def root():
    return {"message": "Welcome to Event Management APP. We make your event glamorous"}