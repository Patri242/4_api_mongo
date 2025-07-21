from fastapi import HTTPException
#como vamos a conectar con BBDD tengo que importar la conexion
from db.mongo import book_collection
from models.book_models import Book, BookCreate


#vamos a crear una funcion que nos permita convertir el tipo de mongo (objeto) en una clase (class) Book de python. Se va a llamar book_helper y va a transformar los datos de python a mongo. nuestra propia funcion de parseo.


def book_helper(book:dict) -> Book:
    return Book(
        id=str(book["_id"]),
        title=book["title"],  #hablando de un diccionario
        author=book["author"], 
        year=book["year"], 
        pages=book.get("pages"), #si el campo es opcional que no me de error, instead; 'null'
    )


#controlador post para crear un libro en mongo
async def create_book(book: BookCreate):
    try:
        new_book = book.model_dump() #lo convierte en un diccionario
        result= await book_collection.insert_one(new_book)
        book_created = await book_collection.find_one({"_id": result .inserted_id})
        return book_helper(book_created)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")