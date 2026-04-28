import streamlit as st
import pandas as pd
import requests

# === CONFIGURACIÓN ===
SHEETDB_API_URL = "https://sheetdb.io/api/v1/vehoumph81svs"
CLAVE_DOCENTE = "docentejwts123"

equipos_estudiantes = {
    "Selecciona tu equipo":[],
    "Equipo 1": ["Selecciona tu nombre", "Deans Cabrera", "Miguel Herrera", "Eleana Navio", "Deisy Salazar", "Gianfranco Vaccari"],
    "Equipo 2": ["Daniel Pinedo", "Jorge Acero", "Milagro Molina", "Sergio Valencia", "Yoseff Vilcapoma"],
    "Equipo 3": ["Andrés Álvarez", "Jacklyn Beraún", "Oscar Garnique", "Rafael Marca", "Nohelia Tang", "Jessica Timana"]
}

def guardar_evaluacion(datos):
    payload = {"data": datos}
    response = requests.post(SHEETDB_API_URL, json=payload)
    return response.status_code == 201 or response.status_code == 200

def obtener_evaluaciones():
    response = requests.get(SHEETDB_API_URL)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return pd.DataFrame()

# Interfaz principal
st.title("🎓 Aplicación de Coevaluación Grupal")

modo = st.sidebar.selectbox("Seleccione modo", ["Estudiante", "Docente"])

if modo == "Estudiante":
    st.header("📝 Formulario de Coevaluación")

    # 1. Inicializar el estado de envío para evitar duplicados
    if "enviado" not in st.session_state:
        st.session_state.enviado = False

    # 2. Si ya se envió, ocultamos el formulario y mostramos mensaje
    if st.session_state.enviado:
        st.success("✅ Evaluación enviada correctamente. Gracias por participar.")
        if st.button("Enviar otra respuesta"):
            st.session_state.enviado = False
            st.rerun()
    else:
        equipo_seleccionado = st.selectbox("", options=list(equipos_estudiantes.keys()))

        if equipo_seleccionado:
            integrantes = equipos_estudiantes[equipo_seleccionado]
            evaluador = st.selectbox("Tu Nombre", options=integrantes)

            st.write("### Califica a cada compañero (incluyéndote):")
            notas = {}
            for nombre in integrantes:
                nota = st.slider(f"Nota para {nombre}", min_value=0.0, max_value=20.0, step=0.5, key=f"nota_{nombre}")
                notas[nombre] = nota

            # El botón de enviar
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
                    
                    if guardar_evaluacion(datos):
                        st.session_state.enviado = True
                        st.rerun()
                    else:
                        st.error("Error al enviar los datos. Inténtalo de nuevo.")

elif modo == "Docente":
    st.header("🔐 Acceso al Modo Docente")
    
    if "acceso_docente" not in st.session_state:
        st.session_state["acceso_docente"] = False

    if not st.session_state["acceso_docente"]:
        clave_ingresada = st.text_input("Ingrese la contraseña", type="password")
        if st.button("Ingresar"):
            if clave_ingresada == CLAVE_DOCENTE:
                st.session_state["acceso_docente"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    else:
        st.success("🔓 Acceso concedido.")
        
        # Corregido: Obtener datos de la API en lugar de un archivo Excel local
        df = obtener_evaluaciones()

        if df.empty:
            st.info("No hay evaluaciones registradas aún.")
        else:
            st.subheader("Todas las Evaluaciones")
            st.dataframe(df)

            st.subheader("Promedio por Estudiante")
            df["Nota"] = pd.to_numeric(df["Nota"])
            promedios = df.groupby("Estudiante")["Nota"].mean().round(2).reset_index()
            promedios["Factor Ajuste"] = (promedios["Nota"] / 20).round(2)
            st.dataframe(promedios)

            if st.button("Cerrar Sesión"):
                st.session_state["acceso_docente"] = False
                st.rerun()










