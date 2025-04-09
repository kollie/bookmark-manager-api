from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, bookmark, user
from database import Base, engine


# Initialize the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bookmark Manager API",
    description="A RESTful API for managing bookmarks with user authentication",
    version="1.0.0"
)

# Configure CORS middleware to allow requests from any origin.
# In production, you may want to restrict allowed origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider replacing "*" with a list of trusted origins in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# async def startup_event():
#     """
#     Event handler that initializes the database on application startup.

#     This function is called when the application starts and will run the
#     init_db() function to create tables and run any pending migrations.
#     """
#     init_db()

# Include API routers with proper versioning and categorization
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(user.router, prefix="/api/v1", tags=["Users"])
app.include_router(bookmark.router, prefix="/api/v1", tags=["Bookmarks"])

@app.get("/")
async def root():
    """
    Root endpoint returning a welcome message.

    Returns:
        dict: A simple message confirming that the API is running.
    """
    return {"message": "Welcome to the Bookmark Manager API"}
