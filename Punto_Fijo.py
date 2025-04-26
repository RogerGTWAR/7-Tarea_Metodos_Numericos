from flask import Blueprint, request, jsonify
import math
import re
import mysql.connector

puntofijo_bp = Blueprint('punto_fijo', __name__)

@puntofijo_bp.route('/punto-fijo', methods=['POST'])
def ejecutar_punto_fijo():
    try:
        funcion = request.form['funcion']
        xi = float(request.form['x0'])
        es = float(request.form['es'])
        ejercicio = request.form['ejercicio']
        max_iter = 100

        def aplicar_reemplazos(s):
            s = s.replace("raiz", "sqrt")
            s = s.replace("sen", "sin")
            s = s.replace("cos", "cos")
            s = s.replace("tan", "tan")
            s = s.replace("atan", "atan")
            s = s.replace("^", "**")
            s = s.replace("e", "exp")
            return s

        funcion = aplicar_reemplazos(funcion)

        allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("__")}
        allowed_names["x"] = 0

        def g(x):
            allowed_names["x"] = x
            return eval(funcion, {"__builtins__": None}, allowed_names)

        resultados = []
        i = 1
        x1 = g(xi)
        ea = 0
        resultados.append((int(ejercicio), i, xi, x1, ea))

        i += 1
        while i <= max_iter:
            xi_old = xi
            xi = x1
            x1 = g(xi)
            ea = abs((x1 - xi) / x1) * 100 if x1 != 0 else 0
            resultados.append((int(ejercicio), i, xi, x1, round(ea, 6)))
            if ea < es:
                break
            i += 1

        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_punto_fijo WHERE ejercicio = %s", (ejercicio,))
        for fila in resultados:
            cursor.execute("""
                INSERT INTO metodo_punto_fijo 
                (ejercicio, iteracion, xi, gxi, ea)
                VALUES (%s, %s, %s, %s, %s)
            """, fila)

        conn.commit()
        cursor.close()
        conn.close()

        return "✅ Cálculos de punto fijo realizados y guardados correctamente."

    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@puntofijo_bp.route('/resultados-punto-fijo')
def ver_resultados_punto_fijo():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ejercicio, iteracion, xi, gxi, ea
            FROM metodo_punto_fijo
            ORDER BY ejercicio ASC, iteracion ASC
        """)
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(filas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@puntofijo_bp.route('/eliminar-punto-fijo/<int:ejercicio>', methods=['DELETE'])
def eliminar_punto_fijo(ejercicio):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_punto_fijo WHERE ejercicio = %s", (ejercicio,))
        conn.commit()
        cursor.close()
        conn.close()
        return f"Registros del ejercicio #{ejercicio} eliminados correctamente."
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@puntofijo_bp.route('/actualizar-punto-fijo', methods=['POST'])
def actualizar_punto_fijo():
    ejercicio = int(request.form['ejercicio'])

    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM metodo_punto_fijo WHERE ejercicio = %s", (ejercicio,))
    conn.commit()
    cursor.close()
    conn.close()

    request.form = request.form.copy()
    request.form['ejercicio'] = str(ejercicio)

    return ejecutar_punto_fijo()
