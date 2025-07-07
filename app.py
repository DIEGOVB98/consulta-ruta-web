
from flask import Flask, request, render_template_string
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

# Cargar la base de datos procesada
file_path = "DATA_PARA_ANALIZAR.xlsx"
df = pd.read_excel(file_path, sheet_name="BASE_DE_DATOS_DEP")
df["ID RUTA "] = df["ID RUTA "].astype(str).str.strip()

# Crear diccionario de días por ruta
df_rsierra = pd.read_excel(file_path, sheet_name="RSierra")
df_rsierra["ID RUTA"] = df_rsierra["ID RUTA"].astype(str).str.strip()
dias_semana = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sábado"]
ruta_dias = {}

for _, row in df_rsierra.iterrows():
    ruta = row["ID RUTA"]
    if pd.notna(ruta):
        dias = [dia for dia in dias_semana if str(row.get(dia)).strip().lower() in ['x', 'xdemanda']]
        ruta_dias[ruta] = dias

# Unir los datos
df["DIAS DE RUTA"] = df["ID RUTA "].map(ruta_dias)
df["ESTABLECIMIENTO"] = df["ESTABLECIMIENTO"].astype(str).str.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        codigo = request.form['codigo'].strip()
        row = df[df["ESTABLECIMIENTO"] == codigo]

        if row.empty:
            result = "<b>El código no existe. Consultar ruta con el equipo de soporte logística.</b>"
        else:
            dias_ruta = row.iloc[0]["DIAS DE RUTA"]
            hoy = datetime.now()
            hoy_nombre = hoy.strftime('%A')
            manana_nombre = (hoy + timedelta(days=1)).strftime('%A')

            traductor_dias = {
                "Monday": "Lunes",
                "Tuesday": "Martes",
                "Wednesday": "Miercoles",
                "Thursday": "Jueves",
                "Friday": "Viernes",
                "Saturday": "Sábado",
                "Sunday": "Domingo"
            }

            hoy_espanol = traductor_dias[hoy_nombre]
            manana_espanol = traductor_dias[manana_nombre]

            # Prioridad: alta si la ruta es mañana, media en otro caso
            prioridad = "Alta" if manana_espanol in dias_ruta else "Media"

            # Mostrar mensaje adicional solo si hoy es día de ruta
            mensaje_extra = ""
            if hoy_espanol in dias_ruta:
                otros_dias = [dia for dia in dias_ruta if dia != hoy_espanol]
                mensaje_extra = f"<br><b>Este cliente tiene una ruta el día de hoy.</b> Consultar a soporte logística si saldrá hoy mismo o se pasa a la ruta de: {', '.join(otros_dias)}."

            result = f"<b>Días de ruta:</b> {', '.join(dias_ruta)}<br><b>Prioridad:</b> {prioridad}{mensaje_extra}"

    return render_template_string('''
        <form method="post">
            Ingrese código de cliente: <input name="codigo">
            <input type="submit" value="Consultar">
        </form>
        <div style="margin-top:20px;">{{ result|safe }}</div>
    ''', result=result)

if __name__ == "__main__":
    app.run(debug=True)
