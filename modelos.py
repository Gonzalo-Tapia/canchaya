# =========================================================================
# modelos.py — Base de datos de CanchaYa con el ORM peewee.
# Responsable: [LEA] Leandro Licata.
# -------------------------------------------------------------------------
# Define las tablas (complejos, usuarios y reservas) como clases de peewee y
# la lógica de horarios: qué turnos tiene un complejo y cuáles siguen libres.
# La base es un archivo SQLite (canchaya.db) que se crea solo al arrancar,
# con los complejos de ejemplo cargados. No se sube al repo (.gitignore).
# =========================================================================

import os
from datetime import datetime, timedelta, timezone

from peewee import (
    SqliteDatabase, Model, CharField, IntegerField, TextField,
    DateField, DateTimeField, ForeignKeyField,
)

RUTA_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "canchaya.db")

# foreign_keys=1 hace que SQLite respete las relaciones entre tablas.
db = SqliteDatabase(RUTA_BASE, pragmas={"foreign_keys": 1})

# Hora de Mendoza (UTC-3, sin horario de verano). Se fija a mano porque el
# servidor de Render corre en UTC y Windows no trae la base de zonas horarias.
ZONA_MENDOZA = timezone(timedelta(hours=-3))

DIAS_DE_ANTICIPACION = 60  # hasta cuántos días adelante se puede reservar

CONFIRMADA = "confirmada"
EN_ESPERA = "espera"
CANCELADA = "cancelada"  # la cancela el usuario desde Mis reservas ([FED])


class ModeloBase(Model):
    class Meta:
        database = db


class Complejo(ModeloBase):
    nombre = CharField(unique=True)
    zona = CharField()
    cantidad_canchas = IntegerField()
    caracteristicas = CharField()          # ej: "techadas", "con vestuarios"
    precio_hora = IntegerField()           # en pesos
    imagen = CharField()                   # archivo dentro de static/assets/images/canchas/
    hora_apertura = IntegerField(default=16)
    hora_cierre = IntegerField(default=24)  # el último turno empieza una hora antes


# Campos propuestos para las cuentas. [FED] los ajusta según sus formularios.
class Usuario(ModeloBase):
    nombre = CharField()
    email = CharField(unique=True)
    clave_hash = CharField()               # nunca la contraseña en texto plano
    creado = DateTimeField(default=datetime.now)


class Reserva(ModeloBase):
    complejo = ForeignKeyField(Complejo, backref="reservas")
    usuario = ForeignKeyField(Usuario, backref="reservas", null=True)  # si reservó con sesión iniciada
    nombre_cliente = CharField()
    email = CharField()
    telefono = CharField()
    fecha = DateField()
    hora = CharField()                     # "HH:MM"
    jugadores = IntegerField()
    comentarios = TextField(default="")
    estado = CharField(default=CONFIRMADA)  # CONFIRMADA, EN_ESPERA o CANCELADA
    creada = DateTimeField(default=datetime.now)


# -------------------------------------------------------------------------
# Horarios y disponibilidad
# -------------------------------------------------------------------------

def ahora_en_mendoza():
    return datetime.now(ZONA_MENDOZA)


def horarios_del_dia(complejo, fecha):
    """Turnos de una hora que todavía se pueden reservar ese día.
    Si la fecha es hoy, se descartan las horas que ya empezaron."""
    ahora = ahora_en_mendoza()
    primera_hora = complejo.hora_apertura
    if fecha == ahora.date():
        primera_hora = max(primera_hora, ahora.hour + 1)
    return [f"{hora:02d}:00" for hora in range(primera_hora, complejo.hora_cierre)]


def horarios_libres(complejo, fecha, horarios):
    """Un turno está libre mientras queden canchas sin reserva confirmada."""
    ocupadas = {}
    confirmadas = Reserva.select(Reserva.hora).where(
        (Reserva.complejo == complejo)
        & (Reserva.fecha == fecha)
        & (Reserva.estado == CONFIRMADA)
    )
    for reserva in confirmadas:
        ocupadas[reserva.hora] = ocupadas.get(reserva.hora, 0) + 1
    return [hora for hora in horarios if ocupadas.get(hora, 0) < complejo.cantidad_canchas]


def validar_fecha_reservable(fecha):
    """Devuelve un mensaje de error si la fecha no se puede reservar, o None."""
    hoy = ahora_en_mendoza().date()
    if fecha < hoy:
        return "La fecha ya pasó. Elegí un día de hoy en adelante."
    if fecha > hoy + timedelta(days=DIAS_DE_ANTICIPACION):
        return f"Solo se puede reservar hasta {DIAS_DE_ANTICIPACION} días adelante."
    return None


# -------------------------------------------------------------------------
# Creación de las tablas y datos iniciales
# -------------------------------------------------------------------------

# Los mismos 6 complejos que mostraba complejos.html en el parcial 1.
COMPLEJOS_INICIALES = [
    {"nombre": "Estadio 5", "zona": "Godoy Cruz", "cantidad_canchas": 3,
     "caracteristicas": "sintéticas", "precio_hora": 18000, "imagen": "cancha1.jpg"},
    {"nombre": "La Redonda", "zona": "Las Heras", "cantidad_canchas": 2,
     "caracteristicas": "techadas", "precio_hora": 20000, "imagen": "cancha2.jpg"},
    {"nombre": "Golazo Fútbol", "zona": "Guaymallén", "cantidad_canchas": 4,
     "caracteristicas": "con parrillas", "precio_hora": 17500, "imagen": "cancha3.jpg"},
    {"nombre": "El Potrero", "zona": "Ciudad", "cantidad_canchas": 2,
     "caracteristicas": "al aire libre", "precio_hora": 15000, "imagen": "cancha4.jpg"},
    {"nombre": "Mundial F5", "zona": "Maipú", "cantidad_canchas": 3,
     "caracteristicas": "con vestuarios", "precio_hora": 19000, "imagen": "cancha5.jpg"},
    {"nombre": "La Bombonerita", "zona": "Luján", "cantidad_canchas": 2,
     "caracteristicas": "iluminadas", "precio_hora": 16500, "imagen": "cancha6.jpg"},
]


def iniciar_base():
    """Crea las tablas que falten y, si no hay complejos, carga los de ejemplo."""
    with db:
        db.create_tables([Complejo, Usuario, Reserva], safe=True)
        if Complejo.select().count() == 0:
            Complejo.insert_many(COMPLEJOS_INICIALES).execute()
