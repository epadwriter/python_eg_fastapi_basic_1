# main.py
from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, auth, error_handlers # Importa nuestros módulos y el nuevo de errores
from app.database import get_db

app = FastAPI(
    title="API de Gestión de Biblioteca",
    description="API RESTful para gestionar libros y usuarios en una biblioteca.",
    version="1.0.0",
)

#Registro de Manejadores de Errores
app.add_exception_handler(HTTPException, error_handlers.http_exception_handler)
app.add_exception_handler(Exception, error_handlers.unhandled_exception_handler)


#Endpoints de Autenticación
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Endpoint para obtener un token de acceso JWT.
    Requiere 'username' y 'password' en el cuerpo de la petición.
    """
    user = auth.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en la base de datos.
    """
    db_user = auth.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nombre de usuario ya registrado")

    return auth.create_db_user(db, user=user)

#Endpoint de Bienvenida
@app.get("/")
async def root():
    return {"mensaje": "¡Bienvenido a la API de tu Biblioteca!"}

#Endpoints de Libros y con autenticación
@app.post("/libros/", response_model=schemas.Libro, status_code=status.HTTP_201_CREATED)
async def crear_libro(
    libro: schemas.LibroCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user) # Ahora devuelve el modelo de DB
):
    """
    Crea un nuevo libro en la base de datos. Requiere autenticación.
    """
    db_libro = models.Libro(**libro.dict())
    db.add(db_libro)
    db.commit()
    db.refresh(db_libro)
    return db_libro

@app.get("/libros/", response_model=List[schemas.Libro])
async def obtener_libros(
    skip: int = 0, limit: int = 100, # NUEVO: Paginación
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Obtiene todos los libros de la base de datos con paginación. Requiere autenticación.
    """
    libros = db.query(models.Libro).offset(skip).limit(limit).all()
    return libros

@app.get("/libros/{libro_id}", response_model=schemas.Libro)
async def obtener_libro_por_id(
    libro_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Obtiene un libro específico por su ID. Requiere autenticación.
    """
    libro = db.query(models.Libro).filter(models.Libro.id == libro_id).first()
    if not libro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    return libro

@app.put("/libros/{libro_id}", response_model=schemas.Libro)
async def actualizar_libro(
    libro_id: int,
    libro_actualizado: schemas.LibroUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Actualiza un libro existente por su ID. Requiere autenticación.
    """
    db_libro = db.query(models.Libro).filter(models.Libro.id == libro_id).first()
    if not db_libro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado para actualizar")

    update_data = libro_actualizado.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_libro, key, value)

    db.add(db_libro)
    db.commit()
    db.refresh(db_libro)
    return db_libro

@app.delete("/libros/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_libro(
    libro_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Elimina un libro por su ID. Requiere autenticación.
    """
    db_libro = db.query(models.Libro).filter(models.Libro.id == libro_id).first()
    if not db_libro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado para eliminar")

    db.delete(db_libro)
    db.commit()
    return # Retorna implícitamente un 204