# =========================================================================
# mis_reservas.py — Página "Mis reservas" de CanchaYa.
# Responsable: [FED] Federico Cabrera.
# -------------------------------------------------------------------------
# Muestra las reservas del usuario con sesión iniciada (Reserva.usuario, que
# api.py ([LEA]) completa con session["usuario_id"]) y permite:
#   GET  /mis-reservas                        lista (próximas y anteriores)
#   POST /mis-reservas/<id>/editar            cambia jugadores y comentarios
#   POST /mis-reservas/<id>/cancelar          cancela la reserva
# No agrega campos al modelo: "cancelada" es un valor más de Reserva.estado.
# Al cancelar una confirmada, el primero en espera de ese turno (FIFO por
# fecha de creación) pasa a confirmada, como promete el formulario de reserva.
# Los formularios validan CSRF igual que cuentas.py (sin CSRFProtect global).
# =========================================================================

from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort

from api import MIN_JUGADORES, MAX_JUGADORES   # mismos límites que la API de [LEA]
from cuentas import csrf_valido
from modelos import db, Reserva, CONFIRMADA, EN_ESPERA, ahora_en_mendoza

mis_reservas = Blueprint("mis_reservas", __name__)

CANCELADA = "cancelada"
LARGO_MAXIMO_COMENTARIOS = 500  # el mismo que valida api.py


def requiere_sesion():
    """Sin sesión, manda a /login y vuelve acá después de ingresar."""
    if g.usuario is None:
        flash("Ingresá a tu cuenta para ver tus reservas.", "aviso")
        return redirect(url_for("cuentas.login", siguiente=request.path))
    return None


def reserva_propia(id_reserva):
    """Devuelve la reserva solo si es del usuario logueado; si no, 404
    (no se revela si existe una reserva ajena con ese id)."""
    reserva = Reserva.get_or_none((Reserva.id == id_reserva) & (Reserva.usuario == g.usuario))
    if reserva is None:
        abort(404)
    return reserva


def ya_paso(reserva):
    ahora = ahora_en_mendoza()
    hoy, hora_actual = ahora.date(), f"{ahora.hour:02d}:00"
    return reserva.fecha < hoy or (reserva.fecha == hoy and reserva.hora <= hora_actual)


def promover_espera(reserva):
    """Si se liberó un turno confirmado, pasa a confirmada la primera en espera."""
    siguiente = (Reserva.select()
                 .where((Reserva.complejo == reserva.complejo_id)
                        & (Reserva.fecha == reserva.fecha)
                        & (Reserva.hora == reserva.hora)
                        & (Reserva.estado == EN_ESPERA))
                 .order_by(Reserva.creada, Reserva.id)
                 .first())
    if siguiente is not None:
        siguiente.estado = CONFIRMADA
        siguiente.save()


@mis_reservas.get("/mis-reservas")
def listar():
    redireccion = requiere_sesion()
    if redireccion:
        return redireccion
    reservas = (Reserva.select().where(Reserva.usuario == g.usuario)
                .order_by(Reserva.fecha, Reserva.hora))
    proximas, anteriores = [], []
    for reserva in reservas:
        if ya_paso(reserva) or reserva.estado == CANCELADA:
            anteriores.append(reserva)
        else:
            proximas.append(reserva)
    anteriores.reverse()  # las más recientes primero
    return render_template("mis_reservas.html", proximas=proximas, anteriores=anteriores,
                           min_jugadores=MIN_JUGADORES, max_jugadores=MAX_JUGADORES)


@mis_reservas.post("/mis-reservas/<int:id_reserva>/editar")
def editar(id_reserva):
    redireccion = requiere_sesion()
    if redireccion:
        return redireccion
    reserva = reserva_propia(id_reserva)
    if not csrf_valido():
        flash("El formulario venció. Recargá la página e intentá de nuevo.", "error")
    elif reserva.estado == CANCELADA or ya_paso(reserva):
        flash("Esa reserva ya no se puede modificar.", "error")
    else:
        comentarios = request.form.get("comentarios", "").strip()
        try:
            jugadores = int(request.form.get("jugadores", ""))
        except ValueError:
            jugadores = None
        if jugadores is None or not MIN_JUGADORES <= jugadores <= MAX_JUGADORES:
            flash(f"La cantidad de jugadores va de {MIN_JUGADORES} a {MAX_JUGADORES}.", "error")
        elif len(comentarios) > LARGO_MAXIMO_COMENTARIOS:
            flash("Los comentarios no pueden superar los 500 caracteres.", "error")
        else:
            reserva.jugadores, reserva.comentarios = jugadores, comentarios
            reserva.save()
            flash("Listo, guardamos los cambios de tu reserva.", "exito")
    return redirect(url_for("mis_reservas.listar"))


@mis_reservas.post("/mis-reservas/<int:id_reserva>/cancelar")
def cancelar(id_reserva):
    redireccion = requiere_sesion()
    if redireccion:
        return redireccion
    reserva = reserva_propia(id_reserva)
    if not csrf_valido():
        flash("El formulario venció. Recargá la página e intentá de nuevo.", "error")
    elif reserva.estado == CANCELADA or ya_paso(reserva):
        flash("Esa reserva ya no se puede cancelar.", "error")
    else:
        with db.atomic():
            estaba_confirmada = reserva.estado == CONFIRMADA
            reserva.estado = CANCELADA
            reserva.save()
            if estaba_confirmada:
                promover_espera(reserva)
        flash("Cancelaste la reserva. Si había alguien en espera, el turno pasó a su nombre.", "exito")
    return redirect(url_for("mis_reservas.listar"))
