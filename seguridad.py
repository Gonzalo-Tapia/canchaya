"""seguridad.py - Medidas de seguridad de CanchaYa.

Activa, con una sola llamada a iniciar_seguridad(app):
  - Proteccion CSRF (flask-wtf)
  - Cabeceras de seguridad (CSP, X-Frame-Options, etc.)
  - Limite de intentos contra fuerza bruta (flask-limiter)
  - Configuracion segura de la cookie de sesion
  - ProxyFix para que el limiter vea la IP real detras del proxy de Render

Los objetos `csrf` y `limiter` quedan a nivel de modulo para que otros
archivos puedan importarlos:  from seguridad import limiter
"""
import os

from flask import flash, jsonify, redirect, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

csrf = CSRFProtect()
limiter = Limiter(get_remote_address, storage_uri="memory://")

CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' https://fonts.googleapis.com; "
    "font-src https://fonts.gstatic.com; "
    "img-src 'self'; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'none'"
)

CABECERAS = {
    "Content-Security-Policy": CSP,
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "same-origin",
    "Permissions-Policy": "microphone=(self), camera=(), geolocation=()",
}


def _es_api():
    """True si el pedido va dirigido a la API JSON (/api...)."""
    return request.path.startswith("/api")


def _responder_error(mensaje, codigo):
    """JSON para /api; para el resto, un flash y vuelta a la pagina anterior."""
    if _es_api():
        return jsonify({"error": mensaje}), codigo
    flash(mensaje, "error")
    return redirect(request.referrer or "/")


def iniciar_seguridad(app):
    """Activa todas las medidas. Llamar despues de definir app.secret_key."""
    # En Render existe la variable RENDER (y cargamos SECRET_KEY a mano);
    # en local no hay ninguna de las dos, y ahi no hay https.
    en_produccion = bool(os.environ.get("RENDER") or os.environ.get("SECRET_KEY"))

    # --- Cookie de sesion ---------------------------------------------------
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=en_produccion,  # solo con https (Render)
    )

    # --- Proxy de Render: que el limiter vea la IP real de cada usuario -----
    if en_produccion:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    # --- CSRF y limiter -----------------------------------------------------
    csrf.init_app(app)
    limiter.init_app(app)

    # --- Manejadores de error -------------------------------------------------
    @app.errorhandler(CSRFError)
    def error_csrf(e):
        return _responder_error(
            "No pudimos validar el formulario. Recargá la página e intentá de nuevo.",
            400,
        )

    @app.errorhandler(429)
    def demasiados_intentos(e):
        return _responder_error("Demasiados intentos, esperá un minuto.", 429)

    # --- Cabeceras de seguridad en todas las respuestas -----------------------
    @app.after_request
    def agregar_cabeceras(respuesta):
        for nombre, valor in CABECERAS.items():
            respuesta.headers[nombre] = valor
        return respuesta