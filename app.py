from flask import Flask, render_template

# Importamos el blueprint que acabamos de crear
from rutas import rutas_globales 

app = Flask(__name__)

app.secret_key = "mi_secreto_super_seguro_ingenero_taurus"

# REGISTRAMOS EL BLUEPRINT
# Le decimos al Gerente: "Contrata a este empleado para que maneje las rutas"
app.register_blueprint(rutas_globales)

# MANEJO DE ERROR 404 (Página no encontrada)
@app.errorhandler(404)
def pagina_no_encontrada(e):
    # Nota el '404' al final, es el código de estado HTTP
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)