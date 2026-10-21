/* =========================================================================
   reservar.js — Conecta el formulario de reserva con la API del backend.
   Responsable: [LEA] Leandro Licata (Frontend / Formularios).
   -------------------------------------------------------------------------
   La página la sirve el mismo servidor Flask del sitio (app.py), así que la API
   se pide en la misma dirección (/api), sin CORS. Esta página le pide los
   complejos y los horarios libres, y le envía la reserva. Si el servidor no
   responde, se avisa en pantalla.
   La validación de HTML5 sigue funcionando: el evento "submit" solo se dispara
   cuando el navegador ya aceptó todos los campos.
   ------------------------------------------------------------------------- */

const API_URL = "/api";

const formulario     = document.querySelector(".formulario");
const selectComplejo = document.querySelector("#complejo");
const inputFecha     = document.querySelector("#fecha");
const selectHora     = document.querySelector("#hora");
const botonEnviar    = formulario.querySelector('button[type="submit"]');
const cajaMensaje    = document.querySelector("#mensaje");

const SIN_CONEXION = "No pudimos conectarnos con el servidor de reservas. " +
                     "Probá de nuevo en unos minutos.";


// 1) Hace un pedido a la API y devuelve { ok, status, datos }.
//    Si el servidor no está levantado, fetch lanza un error que se maneja afuera.
async function pedirApi(ruta, opciones) {
  const respuesta = await fetch(API_URL + ruta, opciones);
  const datos = await respuesta.json();
  return { ok: respuesta.ok, status: respuesta.status, datos: datos };
}


// 2) Muestra un mensaje debajo del botón. tipo: "exito", "aviso" o "error".
//    Se usa textContent (y no innerHTML) para que nada de lo que venga del
//    servidor pueda inyectar HTML en la página.
function mostrarMensaje(texto, tipo) {
  cajaMensaje.textContent = texto;
  cajaMensaje.className = "mensaje mensaje-" + tipo;
  cajaMensaje.hidden = false;
}


// 3) Arma una <option> para un <select>.
function crearOpcion(valor, texto) {
  const opcion = document.createElement("option");
  opcion.value = valor;
  opcion.textContent = texto;
  return opcion;
}


// 4) Fecha de hoy en formato AAAA-MM-DD (hora local, no UTC), para que el
//    calendario no deje elegir días pasados.
function hoy() {
  const fecha = new Date();
  const mes = String(fecha.getMonth() + 1).padStart(2, "0");
  const dia = String(fecha.getDate()).padStart(2, "0");
  return fecha.getFullYear() + "-" + mes + "-" + dia;
}


// 5) Carga los complejos en el <select> desde GET /api/complejos.
async function cargarComplejos() {
  try {
    const { datos } = await pedirApi("/complejos");
    selectComplejo.replaceChildren(crearOpcion("", "— Elegí un complejo —"));
    for (const complejo of datos) {
      const texto = complejo.nombre + " (" + complejo.zona + ") — $ " +
                    complejo.precio_hora.toLocaleString("es-AR") + " / hora";
      selectComplejo.append(crearOpcion(complejo.id, texto));
    }
  } catch (error) {
    selectComplejo.replaceChildren(crearOpcion("", "No se pudieron cargar"));
    botonEnviar.disabled = true;
    mostrarMensaje(SIN_CONEXION, "error");
  }
}


// 6) Al elegir complejo y fecha, pide los horarios libres y arma el <select>.
//    Los ocupados se pueden elegir igual: es la forma de anotarse en la lista
//    de espera, como en la consola.
async function actualizarHorarios() {
  if (!selectComplejo.value || !inputFecha.value) return;
  const elegido = selectHora.value;
  const ruta = "/complejos/" + selectComplejo.value +
               "/disponibilidad?fecha=" + inputFecha.value;
  try {
    const { ok, datos } = await pedirApi(ruta);
    if (!ok) return mostrarMensaje(datos.error, "error");
    selectHora.replaceChildren(crearOpcion("", "— Elegí un horario —"));
    for (const hora of datos.horarios) {
      const libre = datos.libres.includes(hora);
      const texto = libre ? hora : hora + " (ocupado: lista de espera)";
      selectHora.append(crearOpcion(hora, texto));
    }
    selectHora.value = elegido;  // conserva la elección si sigue en la lista
  } catch (error) {
    mostrarMensaje(SIN_CONEXION, "error");
  }
}


// 7) Lee el formulario y arma el JSON con los nombres de campo del backend.
//    id_complejo y jugadores van como números: la API rechaza "10" como texto.
function leerFormulario(aceptarEspera) {
  const campos = new FormData(formulario);
  return {
    nombre_cliente: campos.get("nombre_cliente").trim(),
    email:          campos.get("email").trim(),
    telefono:       campos.get("telefono").trim(),
    id_complejo:    Number(campos.get("id_complejo")),
    fecha:          campos.get("fecha"),
    hora:           campos.get("hora"),
    jugadores:      Number(campos.get("jugadores")),
    comentarios:    campos.get("comentarios").trim(),
    aceptar_espera: aceptarEspera
  };
}


// 8) Mensaje para una reserva creada, según si quedó confirmada o en espera.
function mensajeReserva(reserva) {
  const [anio, mes, dia] = reserva.fecha.split("-");
  const turno = dia + "/" + mes + " a las " + reserva.hora;
  if (reserva.estado === "confirmada") {
    return "¡Listo! Tu reserva #" + reserva.id + " para el " + turno +
           " está confirmada. Te esperamos.";
  }
  return "Quedaste en la lista de espera para el " + turno + " (reserva #" +
         reserva.id + "). Si el turno se libera, pasa a tu nombre.";
}


// 9) Si el horario está ocupado, ofrece anotarse en la lista de espera.
function ofrecerEspera(texto) {
  mostrarMensaje(texto, "aviso");
  const boton = document.createElement("button");
  boton.type = "button";
  boton.className = "boton boton-primario";
  boton.textContent = "Anotarme en la lista de espera";
  boton.addEventListener("click", () => enviarReserva(true));
  cajaMensaje.append(boton);
}


// 10) Envía la reserva con POST /api/reservas y muestra el resultado.
async function enviarReserva(aceptarEspera) {
  botonEnviar.disabled = true;  // evita reservas duplicadas por doble clic
  try {
    const { ok, status, datos } = await pedirApi("/reservas", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(leerFormulario(aceptarEspera))
    });
    if (ok) {
      mostrarMensaje(mensajeReserva(datos), datos.estado === "confirmada" ? "exito" : "aviso");
      formulario.reset();
      selectHora.replaceChildren(crearOpcion("", "— Elegí complejo y fecha —"));
    } else if (status === 409) {
      ofrecerEspera(datos.error);
    } else {
      mostrarMensaje(datos.error, "error");
    }
  } catch (error) {
    mostrarMensaje(SIN_CONEXION, "error");
  }
  botonEnviar.disabled = false;
}


// 11) Conexión de los eventos y carga inicial.
inputFecha.min = hoy();
selectComplejo.addEventListener("change", actualizarHorarios);
inputFecha.addEventListener("change", actualizarHorarios);
formulario.addEventListener("submit", (evento) => {
  evento.preventDefault();  // la página no se recarga: el envío lo hace fetch
  enviarReserva(false);
});
cargarComplejos();
