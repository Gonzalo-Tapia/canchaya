# =========================================================================
# app.py — Servidor web Flask de CanchaYa.
# Responsable: [LEA] Leandro Licata.
# -------------------------------------------------------------------------
# Sirve las páginas del sitio (plantillas Jinja en templates/) y los archivos
# estáticos (static/). Por ahora solo muestra las mismas 4 páginas del primer
# parcial; los modelos, la API y la seguridad se suman en los próximos pasos.
# =========================================================================

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/complejos")
def complejos():
    return render_template("complejos.html")


@app.route("/reservar")
def reservar():
    return render_template("reservar.html")


@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")


if __name__ == "__main__":
    app.run(debug=True)
