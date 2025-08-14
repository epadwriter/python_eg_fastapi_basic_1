# tests/test_main.py

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

#from app.main import app
from app.main import app

from app.database import Base, get_db
from app.models import User, Libro
from app.auth import get_current_user, get_password_hash
from sqlalchemy.orm import Session


# --- Configuración de la Base de Datos para Pruebas ---
# Usamos una base de datos SQLite en memoria para las pruebas,
# para que no afecte tu base de datos MySQL real.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool, # Necesario para SQLite en memoria con múltiples hilos
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session")
def db_session_fixture():
    """
    Fixture de Pytest para una sesión de base de datos aislada para cada prueba.
    """
    Base.metadata.create_all(bind=engine) # Crea las tablas para la prueba
    db = TestingSessionLocal()
    try:
        yield db # Proporciona la sesión de DB a la prueba
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine) # Elimina las tablas después de la prueba (limpieza)

# --- Sobrescribir la Dependencia get_db para usar la DB de prueba ---
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# --- Fixture para el cliente de prueba de FastAPI ---
client = TestClient(app)

# --- Fixture para un usuario de prueba autenticado ---
@pytest.fixture(name="test_user")
def test_user_fixture(db_session: Session):
    """
    Crea un usuario de prueba en la DB para autenticación.
    """
    hashed_password = get_password_hash("testpass")
    user = User(username="testuser", hashed_password=hashed_password, is_active=True)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user: User):
    """
    Fixture para obtener cabeceras de autorización con un token para 'testuser'.
    """
    response = client.post("/token", data={"username": "testuser", "password": "testpass"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# --- Pruebas de los Endpoints ---

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"mensaje": "¡Bienvenido a la API de tu Biblioteca!"}

def test_create_user(db_session: Session):
    response = client.post(
        "/users/",
        json={"username": "newuser", "password": "newpass"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data
    assert "is_active" in data
    # Verificar que el usuario fue realmente creado en la DB
    user_in_db = db_session.query(User).filter(User.username == "newuser").first()
    assert user_in_db is not None
    assert user_in_db.username == "newuser"

def test_create_existing_user(db_session: Session):
    # Crea un usuario primero
    client.post("/users/", json={"username": "existinguser", "password": "pass"})
    # Intenta crearlo de nuevo
    response = client.post(
        "/users/",
        json={"username": "existinguser", "password": "pass"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Nombre de usuario ya registrado"}

def test_login_for_access_token(test_user: User):
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    response = client.post(
        "/token",
        data={"username": "wronguser", "password": "wrongpass"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Credenciales incorrectas"}

def test_create_libro(auth_headers: dict):
    response = client.post(
        "/libros/",
        headers=auth_headers,
        json={
            "titulo": "El Señor de los Anillos",
            "autor": "J.R.R. Tolkien",
            "anio_publicacion": 1954,
            "genero": "Fantasía"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == "El Señor de los Anillos"
    assert "id" in data

def test_get_libros(auth_headers: dict):
    # Primero crea un libro
    client.post(
        "/libros/",
        headers=auth_headers,
        json={
            "titulo": "1984",
            "autor": "George Orwell",
            "anio_publicacion": 1949,
            "genero": "Distopía"
        },
    )
    response = client.get("/libros/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["titulo"] == "1984"

def test_get_libro_by_id(auth_headers: dict):
    # Primero crea un libro
    create_response = client.post(
        "/libros/",
        headers=auth_headers,
        json={
            "titulo": "Don Quijote de la Mancha",
            "autor": "Miguel de Cervantes",
            "anio_publicacion": 1605,
            "genero": "Novela"
        },
    )
    libro_id = create_response.json()["id"]

    response = client.get(f"/libros/{libro_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["titulo"] == "Don Quijote de la Mancha"

def test_get_nonexistent_libro(auth_headers: dict):
    response = client.get("/libros/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Libro no encontrado"}

def test_update_libro(auth_headers: dict):
    # Crea un libro para actualizar
    create_response = client.post(
        "/libros/",
        headers=auth_headers,
        json={
            "titulo": "Un libro viejo",
            "autor": "Autor viejo",
            "anio_publicacion": 2000,
            "genero": "Drama"
        },
    )
    libro_id = create_response.json()["id"]

    update_data = {
        "titulo": "Un libro actualizado",
        "genero": "Comedia",
        "disponible": False
    }
    response = client.put(f"/libros/{libro_id}", headers=auth_headers, json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == "Un libro actualizado"
    assert data["genero"] == "Comedia"
    assert data["disponible"] is False
    assert data["autor"] == "Autor viejo" # Autor no cambió

def test_delete_libro(auth_headers: dict):
    # Crea un libro para eliminar
    create_response = client.post(
        "/libros/",
        headers=auth_headers,
        json={
            "titulo": "Libro a eliminar",
            "autor": "Autor de prueba",
            "anio_publicacion": 2020,
            "genero": "Misterio"
        },
    )
    libro_id = create_response.json()["id"]

    response = client.delete(f"/libros/{libro_id}", headers=auth_headers)
    assert response.status_code == 204 # No Content

    # Verifica que el libro fue eliminado
    get_response = client.get(f"/libros/{libro_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_delete_nonexistent_libro(auth_headers: dict):
    response = client.delete("/libros/999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Libro no encontrado para eliminar"}

def test_unauthorized_access():
    # Intenta acceder a un endpoint protegido sin token
    response = client.get("/libros/")
    assert response.status_code == 401
    assert response.json() == {"detail": "No se pudieron validar las credenciales"}

    # Intenta crear un libro sin token
    response = client.post("/libros/", json={"titulo": "Unauthorized", "autor": "No one", "anio_publicacion": 2023, "genero": "Terror"})
    assert response.status_code == 401

    