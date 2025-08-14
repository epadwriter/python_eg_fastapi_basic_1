# schemas.py
from pydantic import BaseModel, Field
from typing import Optional

# --- Modelos para Usuarios ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50) # Añadimos validación
class UserCreate(UserBase):
    password: str = Field(..., min_length=6) # Mínima longitud para password

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

# --- Modelos para Libros ---
class LibroBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=100)
    autor: str = Field(..., min_length=1, max_length=100)
    anio_publicacion: int = Field(..., gt=1000, lt=2026)
    genero: str = Field(..., min_length=1, max_length=50)
    disponible: bool = True

class LibroCreate(LibroBase):
    pass

class LibroUpdate(BaseModel):
    titulo: Optional[str] = None
    autor: Optional[str] = None
    anio_publicacion: Optional[int] = None
    genero: Optional[str] = None
    disponible: Optional[bool] = None

class Libro(LibroBase):
    id: int

    class Config:
        orm_mode = True

# Modelos para Autenticación (JWT)
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None