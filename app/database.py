# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

#Configuración de Conexión a MySQL
# ¡IMPORTANTE! Reemplaza los valores con los de tu configuración de MySQL.
# Por ejemplo: "mysql+pymysql://usuario:contraseña@host:puerto/nombre_db"
# Si tu MySQL está local y usa el puerto por defecto, podría ser:
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:tu_contraseña_mysql@localhost:3306/biblioteca_db"
# Asegúrate de crear la base de datos 'biblioteca_db' en MySQL manualmente (ej. CREATE DATABASE biblioteca_db;)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:mi_contraseña_de_mysql@localhost:3306/biblioteca_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        