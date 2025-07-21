from fastapi import FastAPI
from routes import book_routes

app = FastAPI() 

#ruta de acceso a los libros
app.include_router(book_routes.router, prefix="/books", tags=['Books'])
