# error_handlers.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Manejador global para excepciones HTTP de FastAPI.
    Formatea la respuesta de error de manera consistente.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Manejador global para excepciones no controladas.
    Captura cualquier error inesperado y devuelve un 500.
    """
    print(f"Error no manejado: {exc}") # Idealmente, esto iría a un sistema de logs
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ocurrió un error interno del servidor. Por favor, inténtalo de nuevo más tarde."},
    )
