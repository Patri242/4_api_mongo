from fastapi import HTTPException
#como vamos a conectar con BBDD tengo que importar la conexion
from db.mongo import book_collection
from models.book_models import Book, BookCreate
from bson import ObjectId #libreria viene con pymongo


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
        result= await book_collection.insert_one(new_book)#insert_many es insertar un array
        book_created = await book_collection.find_one({"_id": result .inserted_id}) #find, update_one, delete_one
        return book_helper(book_created)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
#controlador para obtener la lista de libros
async def get_book_list():
    try:
        books = []
        result= book_collection.find({}) #no puede ser asincrono porque si saltariamos al for sin tener el array cargado
        async for item in result:
            books.append(book_helper(item))
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
#GET obtener un libro por id
async def get_book_by_id(book_id:str):
    try:
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400,detail="El ID del libro no es valido")
        book= await book_collection.find_one({'_id': ObjectId(book_id)})
        if book:
            return book_helper(book)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
#UPDATE 
async def update_book(book_id:str, book_data:BookCreate):
    try:
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="El ID del libro no es valido")
        result = await book_collection.update_one(
            {"_id":ObjectId(book_id)},
            {"$set":book_data.model_dump()}
        )
        if result.modified_count == 0:
            return None
        update = await book_collection.find_one({"_id":ObjectId(book_id)})
        return book_helper(update)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
#DELETE
async def delete_one_book_by_id(book_id:str):
    try:
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail='Id no valido')
        result = await book_collection.delete_one({"_id" : ObjectId(book_id)})
        if not result.deleted_count == 1:
            raise HTTPException(status_code=409 , detail='No se ha podido borrar el libro. Intentalo de nuevo')
        return {'msg':f"El libro con id {book_id} se ha borrado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


