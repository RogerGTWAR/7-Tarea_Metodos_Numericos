from flask import Flask, send_file, send_from_directory
from Biseccion import biseccion_bp
from Falsa_Posicion import falsa_bp

app = Flask(__name__)

# Rutas estáticas
@app.route('/')
def index():
    return send_file("index.html")

@app.route('/style.css')
def estilo():
    return send_from_directory('.', 'style.css')

@app.route('/Funciones.js')
def funciones():
    return send_from_directory('.', 'Funciones.js')

# Registrar blueprints
app.register_blueprint(biseccion_bp)
app.register_blueprint(falsa_bp)

if __name__ == '__main__':
    app.run(debug=True)
