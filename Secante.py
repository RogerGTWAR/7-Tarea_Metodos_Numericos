from flask import Blueprint, request, jsonify
import math
import re
import mysql.connector

secante_bp = Blueprint('secante', __name__)

@secante_bp.route('/secante', methods=['POST'])
def ejecutar_secante():
    try:
        funcion = request.form['funcion']
        x0 = float(request.form['x0'])
        x1 = float(request.form['x1'])
        es = float(request.form['es'])
        ejercicio = request.form['ejercicio']
        max_iter = 100

        def aplicar_reemplazos(f_str):
            f_str = f_str.replace("sen", "sin")
            f_str = f_str.replace("raiz", "sqrt")
            f_str = f_str.replace("ln", "log_ln_")
            f_str = f_str.replace("log(", "log10(")
            f_str = f_str.replace("log_ln_", "log")
            f_str = f_str.replace("arctan", "atan")
            f_str = f_str.replace("arcsin", "asin")
            f_str = f_str.replace("arccos", "acos")
            f_str = f_str.replace("^", "**")
            f_str = re.sub(r'e\*\*(\(?[^\)\+\-\*/]+?\)?)', r'exp(\1)', f_str)
            return f_str

        funcion = aplicar_reemplazos(funcion)

        allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("__")}
        allowed_names["x"] = 0

        def f(x):
            allowed_names["x"] = x
            return eval(funcion, {"__builtins__": None}, allowed_names)

        resultados = []
        i = 1
        ea = 100

        while i <= max_iter:
            fx0 = f(x0)
            fx1 = f(x1)

            if (fx1 - fx0) == 0:
                raise ValueError("División por cero detectada durante el cálculo.")

            x2 = x1 - fx1 * (x1 - x0) / (fx1 - fx0)

            if i == 1:
                ea = 0
            else:
                ea = abs((x2 - x1) / x2) * 100

            resultados.append((int(ejercicio), i, x0, x1, fx0, fx1, x2, round(ea, 6)))

            if ea < es and i > 1:
                break

            x0 = x1
            x1 = x2
            i += 1

        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_secante WHERE ejercicio = %s", (ejercicio,))
        for fila in resultados:
            cursor.execute("""
                INSERT INTO metodo_secante
                (ejercicio, iteracion, xi_1, xi, fxi_1, fxi, xi_t, ea)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, fila)

        conn.commit()
        cursor.close()
        conn.close()

        return "✅ Cálculos de la secante realizados y guardados correctamente."

    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@secante_bp.route('/resultados-secante')
def ver_resultados_secante():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ejercicio, iteracion, xi_1, xi, fxi_1, fxi, xi_t, ea
            FROM metodo_secante
            ORDER BY ejercicio ASC, iteracion ASC
        """)
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(filas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@secante_bp.route('/eliminar-secante/<int:ejercicio>', methods=['DELETE'])
def eliminar_secante(ejercicio):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metodo_secante WHERE ejercicio = %s", (ejercicio,))
        conn.commit()
        cursor.close()
        conn.close()
        return f"Registros del ejercicio #{ejercicio} eliminados correctamente."
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@secante_bp.route('/actualizar-secante', methods=['POST'])
def actualizar_secante():
    ejercicio = int(request.form['ejercicio'])

    conn = mysql.connector.connect(host="localhost", user="root", password="root", database="metodos_numericos")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM metodo_secante WHERE ejercicio = %s", (ejercicio,))
    conn.commit()
    cursor.close()
    conn.close()

    request.form = request.form.copy()
    request.form['ejercicio'] = str(ejercicio)

    return ejecutar_secante()
