//1 
Asegúrate de tener Python y VS Code instalados.

Para conectar Python con MySQL, necesitaremos un conector.

Instala MySQL Server o Xammp

Crea el entorno virtual python. Este nos ayuda a estructurar nuestro proyecto:

python -m venv venv

Activa tu Entorno Virtual:

En Windows: .\venv\Scripts\activate

En macOS/Linux: source venv/bin/activate

Instala las Librerías Necesarias:
pip install "fastapi[all]" uvicorn sqlalchemy pymysql alembic "python-jose[cryptography]" "passlib[bcrypt]" pytest httpx 

//2
Crea la base de datos biblioteca_db en MySql (usa workbench o xammp)

Inicializa alembic:
alembic init alembic

Abre alembic.ini. Busca la línea sqlalchemy.url = y cámbiala a tu URL de MySQL:
sqlalchemy.url = mysql+pymysql://root:tu_contraseña_mysql@localhost:3306/biblioteca_db

También, asegúrate que script_location = alembic.
Finalmente, en alembic/env.py, asegúrate de que target_metadata = Base.metadata

//3

Crear la Primera Migración:
alembic revision --autogenerate -m "create user and libro tables"

Aplicar la Migración:
alembic upgrade head

Esto debió crear las tablas users y libros en tu base de datos MySQL biblioteca_db
Puedes verificar con MySQL Workbench o Xammp, depende la que estés usando. 


