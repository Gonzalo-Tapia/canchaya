# CanchaYa

CanchaYa es una plataforma ficticia diseñada para facilitar la reserva de canchas de fútbol 5 en Mendoza.

## Descripción del Proyecto
Este proyecto fue desarrollado como parte de la práctica profesional para facilitar a los usuarios la búsqueda de complejos deportivos, la consulta de horarios disponibles y la reserva de turnos de manera ágil y sencilla.

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
- HTML5
- CSS3 (con CSS Grid, Flexbox y Variables CSS)
- JavaScript (menú hamburguesa y conexión del formulario con la API)

## Conexión con el backend
El formulario de `reservar.html` usa la API del repositorio **canchaya-backend**
(`js/reservar.js`): carga los complejos, muestra los horarios libres y envía la reserva.
Para probarlo, levantar primero el backend con `python api.py` (puerto 5000) y abrir el
sitio con Live Server o con `python -m http.server 5500`.
