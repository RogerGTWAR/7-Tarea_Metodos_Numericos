from flask import Flask, request, jsonify, send_file
import mysql.connector
import math
from flask import send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return send_file("index.html")

@app.route('/style.css')
def estilo():
    return send_from_directory('.', 'style.css')

@app.route('/Funciones.js')
def funciones():
    return send_from_directory('.', 'Funciones.js')

@app.route('/biseccion', methods=['POST'])
def ejecutar_biseccion():
    try:
        funcion = request.form['funcion']
        xa = float(request.form['xa'])
        xb = float(request.form['xb'])
        es = float(request.form['es'])
        ejercicio = request.form['ejercicio']
        max_iter = 100

        # Reemplazos amigables
        def aplicar_reemplazos(s):
            s = s.replace("raiz", "sqrt")
            s = s.replace("ln", "log_ln_")
            s = s.replace("log(", "log10(")
            s = s.replace("log_ln_", "log")
            s = s.replace("sen", "sin")
            s = s.replace("cos", "cos")
            s = s.replace("tan", "tan")
            s = s.replace("^", "**")
            s = s.replace("e", "exp")
            return s

        funcion = aplicar_reemplazos(funcion)

        # Función evaluadora segura
        allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("__")}
        allowed_names["x"] = 0

        def f(x):
            allowed_names["x"] = x
            return eval(funcion, {"__builtins__": None}, allowed_names)

        # Lista para almacenar los resultados
        resultados = []

        Xr_anterior = 0
        i = 1

        while True:
            fXa = f(xa)
            fXb = f(xb)
            xr = (xa + xb) / 2
            fXr = f(xr)

            ea = 0 if i == 1 else abs((xr - Xr_anterior) / xr) * 100
            resultados.append((int(ejercicio), i, xa, xb, fXa, fXb, xr, fXr, round(ea, 4)))

            if ea < es and i > 1:
                break
            if i >= max_iter:
                break

            Xr_anterior = xr
            if fXa * fXr < 0:
                xb = xr
            else:
                xa = xr
            i += 1

        # Conectar y guardar en la base de datos
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="metodos_numericos"
        )
        cursor = conn.cursor()
        # BORRAR REGISTROS REPETIDOS POR SEGURIDAD
        cursor.execute("DELETE FROM metodo_biseccion WHERE ejercicio = %s", (ejercicio,))

        for fila in resultados:
            cursor.execute("""
                INSERT INTO metodo_biseccion 
                (ejercicio, iteracion, xa, xb, fxa, fxb, xr, fxr, ea)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, fila)

        conn.commit()
        cursor.close()
        conn.close()

        return "✅ Cálculos realizados y guardados correctamente."

    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@app.route('/resultados-biseccion')
def ver_resultados_biseccion():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="metodos_numericos"
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ejercicio, iteracion, xa, xb, fxa, fxb, xr, fxr, ea
            FROM metodo_biseccion
            ORDER BY ejercicio ASC, iteracion ASC
        """)
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(filas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/eliminar-biseccion/<int:ejercicio>', methods=['DELETE'])
def eliminar_biseccion(ejercicio):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="metodos_numericos"
        )
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_biseccion WHERE ejercicio = %s", (ejercicio,))
        conn.commit()
        cursor.close()
        conn.close()
        return f"Registros del ejercicio #{ejercicio} eliminados correctamente."
    except Exception as e:
        return f"❌ Error: {str(e)}", 500
    
@app.route('/actualizar-biseccion', methods=['POST'])
def actualizar_biseccion():
    ejercicio = int(request.form['ejercicio'])

    # Eliminar registros antiguos primero
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="metodos_numericos"
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM metodo_biseccion WHERE ejercicio = %s", (ejercicio,))
    conn.commit()
    cursor.close()
    conn.close()

    # Agrega manualmente el campo 'ejercicio' al request.form (porque es inmutable)
    request.form = request.form.copy()
    request.form['ejercicio'] = str(ejercicio)

    return ejecutar_biseccion()


if __name__ == '__main__':
    app.run(debug=True)

