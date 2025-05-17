import streamlit as st
import pandas as pd
import requests

# === CAMBIA SOLO ESTA LÍNEA CON TU URL DE SHEETDB.IO ===
SHEETDB_API_URL = "https://sheetdb.io/api/v1/vehoumph81svs "

CLAVE_DOCENTE = "docentejwts123"

equipos_estudiantes = {
    "Equipo 1": ["Raul Olaechea", "Fressia", "Paola Errea"],
    "Equipo 2": ["Fiorella Valdivia", "Karla Elescano", "Patricia Sinclair", "Mauricio Negrón"],
    "Equipo 3": ["Alessandra Lavado", "Ericsson Castro", "Antonio Monzón", "Elisabeth Chamorro"],
    "Equipo 4": ["Nina Llamoca", "Elcy Maguiña", "Melany Zevallos", "Javier García","José Tipacti"]
}

def guardar_evaluacion(datos):
    payload = {"data": datos}
    response = requests.post(SHEETDB_API_URL, json=payload)
    return response.status_code == 200

def obtener_evaluaciones():
    response = requests.get(SHEETDB_API_URL)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return pd.DataFrame()

# Interfaz principal (código igual al usado antes)
st.title("🎓 Aplicación de Coevaluación Grupal")

modo = st.sidebar.selectbox("Seleccione modo", ["Estudiante", "Docente"])

if modo == "Estudiante":
    st.header("📝 Formulario de Coevaluación")

    equipo_seleccionado = st.selectbox("Selecciona tu equipo", options=list(equipos_estudiantes.keys()))

    if equipo_seleccionado:
        integrantes = equipos_estudiantes[equipo_seleccionado]
        evaluador = st.selectbox("Tu Nombre", options=integrantes)

        st.write("### Califica a cada compañero (incluyéndote):")
        notas = {}
        for nombre in integrantes:
            nota = st.slider(f"Nota para {nombre}", min_value=0.0, max_value=20.0, step=0.5, key=f"nota_{nombre}")
            notas[nombre] = nota

        if st.button("Enviar Evaluación"):
            if not notas.get(evaluador):
                st.error("Debes calificarte a ti mismo.")
            else:
                datos = []
                for estudiante, nota in notas.items():
                    datos.append({
                        "Equipo": equipo_seleccionado,
                        "Estudiante": estudiante,
                        "Evaluador": evaluador,
                        "Nota": nota
                    })
                guardar_evaluacion(datos)
                st.success("✅ Evaluación enviada correctamente.")

elif modo == "Docente":
    st.header("🔐 Acceso al Modo Docente")
    clave_ingresada = st.text_input("Ingrese la contraseña del docente", type="password")
    if st.button("Ingresar"):
        if clave_ingresada == CLAVE_DOCENTE:
            st.session_state["acceso_docente"] = True
        else:
            st.error("Contraseña incorrecta.")

    if st.session_state.get("acceso_docente", False):
    	st.success("🔓 Acceso concedido al modo docente.")

    	try:
        	df = pd.read_excel(ARCHIVO_EXCEL, sheet_name="Evaluaciones")
    	except Exception as e:
        	st.error("Error al leer el archivo Excel.")
        	df = pd.DataFrame()

    	if df.empty:
        	st.info("No hay evaluaciones registradas aún.")
    	else:
        	st.subheader("Todas las Evaluaciones")
        	st.dataframe(df)

        	st.subheader("Promedio por Estudiante")

        	# Calcular promedio por estudiante (escala 0-20)
        	promedios = df.groupby("Estudiante")["Nota"].mean().round(2).reset_index()
        	promedios.rename(columns={"Nota": "Nota Promedio"}, inplace=True)

        	# Calcular factor de ajuste (promedio / 20)
        	promedios["Factor Ajuste"] = (promedios["Nota Promedio"] / 20).round(2)

        	# Mostrar tabla con ambos valores
        	st.dataframe(promedios)

        	st.download_button(
            		label="📥 Descargar datos",
            		data=open(ARCHIVO_EXCEL, "rb").read(),
            		file_name="coevaluaciones.xlsx",
            		mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        	)

        	if st.button("Cerrar Sesión"):
            		st.session_state["acceso_docente"] = False
            		st.experimental_rerun()
    else:
        st.info("Esperando contraseña...")
