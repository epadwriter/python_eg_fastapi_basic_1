# models.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

# Modelo para la tabla de Usuarios en la base de datos
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True) # String con longitud para MySQL
    hashed_password = Column(String(255)) # String con longitud
    is_active = Column(Boolean, default=True)

# Modelo para la tabla de Libros en la base de datos
class Libro(Base):
    __tablename__ = "libros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), index=True) # String con longitud
    autor = Column(String(100))
    anio_publicacion = Column(Integer)
    genero = Column(String(50))
    disponible = Column(Boolean, default=True)
