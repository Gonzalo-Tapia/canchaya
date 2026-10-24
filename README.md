# CanchaYa

CanchaYa es una plataforma ficticia diseñada para facilitar la reserva de canchas de fútbol 5 en Mendoza.

Proyecto de **Zonda Bytes** para Práctica Profesionalizante I — Tecnicatura Superior en
Desarrollo de Software, Instituto Superior Manuel Belgrano, 2026.

## Descripción del Proyecto
Este proyecto fue desarrollado como parte de la práctica profesional para facilitar a los usuarios la búsqueda de complejos deportivos, la consulta de horarios disponibles y la reserva de turnos de manera ágil y sencilla.

En el primer parcial fue un prototipo estático (HTML, CSS y JS), que quedó guardado en el
tag [`parcial-1`](https://github.com/gustavodipaola75-star/canchaya/tree/parcial-1). En el segundo parcial el sitio pasa a ser servido
por un servidor web Flask con base de datos.

## Funcionalidades principales
- **Inicio:** Sección destacada con llamado a la acción.
- **Reservas:** Formulario interactivo para gestionar turnos.
- **Complejos:** Listado de complejos deportivos disponibles.
- **Nosotros:** Información sobre el equipo de desarrollo.
- **Diseño Responsive:** Adaptabilidad a dispositivos móviles con menú de navegación colapsable.

## Equipo de Desarrollo
- Federico Cabrera (Frontend / HTML)
- Leandro Licata (Frontend / Formularios)
- Gonzalo Tapia (Contenido / UX)
- Gustavo Di Paola (Documentación / Git)

## Tecnologías Utilizadas
- HTML5 con plantillas Jinja
- CSS3 (con CSS Grid, Flexbox y Variables CSS)
- JavaScript (menú hamburguesa y conexión del formulario con la API)
- Python 3.10+ con Flask (servidor web)
- peewee (ORM), flask-wtf y flask-limiter (seguridad), listados en `requirements.txt`

## Estructura

```
app.py            # Servidor Flask: rutas de las páginas
modelos.py        # Base de datos (peewee + SQLite) y lógica de horarios
api.py            # API JSON bajo /api (complejos, disponibilidad, reservas)
templates/        # Plantillas Jinja (base.html + una por página)
static/css/       # Estilos
static/js/        # Lógica de cliente
static/assets/    # Imágenes
requirements.txt  # Dependencias de Python
```

## Cómo se ejecuta

Las dependencias se instalan en un entorno virtual dentro del proyecto (la carpeta `.venv`
está en el `.gitignore`). En PowerShell, desde la carpeta del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

El sitio queda en `http://localhost:5000`. La primera vez se crea sola la base `canchaya.db`
con los complejos de ejemplo; para empezar de cero, alcanza con borrarla. Ya no se abre con Live Server: las páginas son
plantillas Jinja y solo se ven bien servidas por Flask.
