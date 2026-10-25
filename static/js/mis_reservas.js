/* =========================================================================
   mis_reservas.js — Confirmación de cancelar (sin JS inline, compatible con CSP).
   RESPONSABLE: [FED] Federico Cabrera
   ========================================================================= */
for (const form of document.querySelectorAll(".form-cancelar")) {
  form.addEventListener("submit", (evento) => {
    if (!confirm("¿Seguro que querés cancelar esta reserva?")) evento.preventDefault();
  });
}
