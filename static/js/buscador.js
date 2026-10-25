/* =========================================================================
   buscador.js — Buscador y filtros de la página Complejos.
   Responsable: [GON] Gonzalo Tapia (Contenido / UX).
   -------------------------------------------------------------------------
   Lee los data-* de cada tarjeta (los arma complejos.html desde la base) y,
   cada vez que cambia un filtro, muestra solo las que cumplen y las ordena.
   Todo pasa en el navegador: no hace pedidos al servidor.
   ========================================================================= */

// 1) Buscamos en la página los elementos con los que vamos a trabajar.
const grilla      = document.querySelector(".grilla-complejos");
const formulario  = document.querySelector("#buscador");
const campoTexto  = document.querySelector("#filtro-texto");
const selectZona  = document.querySelector("#filtro-zona");
const rangoPrecio = document.querySelector("#filtro-precio");
const valorPrecio = document.querySelector("#valor-precio");
const selectOrden = document.querySelector("#filtro-orden");
const resumen     = document.querySelector("#resumen");
const avisoVacio  = document.querySelector("#sin-resultados");

// 2) Funciones de ayuda.

// Pasa a minúsculas y saca las tildes, para que "guaymallen" encuentre
// "Guaymallén" y "TECHADAS" encuentre "techadas".
// normalize("NFD") separa la letra de su tilde ("é" → "e" + "´") y el
// replace borra esas tildes sueltas.
const normalizar = (texto) =>
  texto.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();

// 20000 → "20.000" (formato argentino).
const formatearPrecio = (numero) => numero.toLocaleString("es-AR");

// 3) Leemos las tarjetas UNA sola vez y armamos una lista de objetos.
//    Así, al filtrar, comparamos datos y no tenemos que leer el HTML cada vez.
const complejos = [...grilla.querySelectorAll(".complejo")].map((elemento, posicion) => ({
  elemento,                                   // la tarjeta en sí, para mostrarla u ocultarla
  posicion,                                   // orden original, para "Sin orden"
  nombre: normalizar(elemento.dataset.nombre),
  zona: elemento.dataset.zona,
  caracteristicas: normalizar(elemento.dataset.caracteristicas),
  precio: Number(elemento.dataset.precio),    // los data-* llegan como texto
}));

// 4) Lee los filtros, decide qué tarjetas se ven y en qué orden.
function aplicarFiltros() {
  const texto = normalizar(campoTexto.value);
  const zona = selectZona.value;               // "" significa "Todas"
  const precioMaximo = Number(rangoPrecio.value);
  const orden = selectOrden.value;

  valorPrecio.textContent = formatearPrecio(precioMaximo);

  // a) Filtrar: se queda con los que cumplen las TRES condiciones.
  const visibles = complejos.filter((c) => {
    const coincideTexto = texto === "" ||
                          c.nombre.includes(texto) ||
                          c.caracteristicas.includes(texto) ||
                          normalizar(c.zona).includes(texto);
    const coincideZona = zona === "" || c.zona === zona;
    const entraEnPrecio = c.precio <= precioMaximo;
    return coincideTexto && coincideZona && entraEnPrecio;
  });

  // b) Ordenar. sort recibe una función que compara de a dos:
  //    si da negativo, "a" va antes que "b".
  if (orden === "menor") {
    visibles.sort((a, b) => a.precio - b.precio);
  } else if (orden === "mayor") {
    visibles.sort((a, b) => b.precio - a.precio);
  } else {
    visibles.sort((a, b) => a.posicion - b.posicion);
  }

  // c) Mostrar: ocultamos todas y después mostramos las que quedaron,
  //    en orden. append() con una tarjeta que ya está en la grilla la MUEVE
  //    al final, así que al recorrerlas en orden quedan ordenadas.
  for (const c of complejos) {
    c.elemento.hidden = true;
  }
  for (const c of visibles) {
    c.elemento.hidden = false;
    grilla.append(c.elemento);
  }

  // d) Resumen y aviso. Siempre textContent, nunca innerHTML (regla del grupo).
  const cantidad = visibles.length;
  resumen.textContent = cantidad === 1 ? "1 complejo" : cantidad + " complejos";
  avisoVacio.hidden = cantidad > 0;
}

// 5) Cada vez que el usuario toca un filtro, se vuelve a aplicar todo.
//    "input" salta en cada tecla o movimiento del rango; "change", al elegir
//    una opción del select.
campoTexto.addEventListener("input", aplicarFiltros);
rangoPrecio.addEventListener("input", aplicarFiltros);
selectZona.addEventListener("change", aplicarFiltros);
selectOrden.addEventListener("change", aplicarFiltros);

// Si apretan Enter en el buscador, que no recargue la página.
formulario.addEventListener("submit", (evento) => evento.preventDefault());

// Primera pasada al cargar, para que aparezca el resumen ("6 complejos").
aplicarFiltros();