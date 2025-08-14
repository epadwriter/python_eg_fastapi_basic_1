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

