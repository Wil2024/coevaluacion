import streamlit as st
import pandas as pd
import requests

# === CONFIGURACIÓN ===
SHEETDB_API_URL = "https://sheetdb.io/api/v1/vehoumph81svs"
CLAVE_DOCENTE = "docentejwts123"

equipos_estudiantes = {
        "Equipo 1": ["Deans Cabrera", "Miguel Herrera", "Eleana Navio", "Deisy Salazar", "Gianfranco Vaccari"],
    "Equipo 2": ["Daniel Pinedo", "Jorge Acero", "Milagro Molina", "Sergio Valencia", "Yoseff Vilcapoma"],
    "Equipo 3": ["Andrés Álvarez", "Jacklyn Beraún", "Oscar Garnique", "Rafael Marca", "Nohelia Tang", "Jessica Timana"]
}

def guardar_evaluacion(datos):
    payload = {"data": datos}
    response = requests.post(SHEETDB_API_URL, json=payload)
    return response.status_code == 201 or response.status_code == 200

def obtener_evaluaciones():
    try:
        response = requests.get(SHEETDB_API_URL)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# Interfaz principal
st.set_page_config(page_title="Sistema de Coevaluación", layout="centered")
st.title("🎓 Aplicación de Coevaluación Grupal")

modo = st.sidebar.selectbox("Seleccione modo", ["Estudiante", "Docente"])

if modo == "Estudiante":
    st.header("📝 Formulario de Coevaluación")

    # Selección de Equipo
    equipo_seleccionado = st.selectbox("1. Selecciona tu equipo", options=["Seleccionar..."] + list(equipos_estudiantes.keys()))

    if equipo_seleccionado != "Seleccionar...":
        integrantes = equipos_estudiantes[equipo_seleccionado]
        evaluador = st.selectbox("2. Selecciona tu Nombre (Evaluador)", options=["Seleccionar..."] + integrantes)

        if evaluador != "Seleccionar...":
            # --- VALIDACIÓN DE DUPLICADOS EN TIEMPO REAL ---
            with st.spinner("Verificando si ya enviaste tu evaluación..."):
                df_registros = obtener_evaluaciones()
            
            ya_envio = False
            if not df_registros.empty and "Evaluador" in df_registros.columns:
                # Comprobar si el nombre ya figura como evaluador
                if evaluador in df_registros["Evaluador"].values:
                    ya_envio = True

            if ya_envio:
                st.error(f"🚫 Lo sentimos, {evaluador}. Ya existe un registro de coevaluación bajo tu nombre.")
                st.info("Para mantener la integridad de los promedios, solo se permite un envío por estudiante.")
            else:
                # Mostrar formulario solo si no ha enviado antes
                st.success(f"Bienvenido {evaluador}. Puedes proceder a calificar a tu equipo (incluyéndote).")
                st.write("---")
                
                notas = {}
                for nombre in integrantes:
                    nota = st.slider(f"Nota para: {nombre}", min_value=0.0, max_value=20.0, step=0.5, key=f"user_{nombre}")
                    notas[nombre] = nota

                # Botón de envío
                if st.button("🚀 Enviar Evaluaciones"):
                    datos_a_enviar = []
                    for estudiante, nota in notas.items():
                        datos_a_enviar.append({
                            "Equipo": equipo_seleccionado,
                            "Estudiante": estudiante,
                            "Evaluador": evaluador,
                            "Nota": nota
                        })
                    
                    if guardar_evaluacion(datos_a_enviar):
                        st.balloons()
                        st.success("✅ Evaluación registrada con éxito. Ya puedes cerrar esta página.")
                        # Al recargar, la validación de arriba detectará el nuevo registro y bloqueará el botón
                        st.button("Finalizar") 
                    else:
                        st.error("Hubo un error de conexión con el servidor. Intenta de nuevo.")

elif modo == "Docente":
    st.header("🔐 Acceso Administrativo")
    
    if "docente_auth" not in st.session_state:
        st.session_state.docente_auth = False

    if not st.session_state.docente_auth:
        pass_input = st.text_input("Contraseña de docente", type="password")
        if st.button("Acceder"):
            if pass_input == CLAVE_DOCENTE:
                st.session_state.docente_auth = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
    else:
        st.subheader("Resultados de Coevaluación")
        df_final = obtener_evaluaciones()

        if not df_final.empty:
            # Asegurar que la columna Nota sea numérica
            df_final["Nota"] = pd.to_numeric(df_final["Nota"], errors='coerce')
            
            st.write("### Resumen por Estudiante")
            # Agrupar por estudiante para obtener el promedio recibido de sus pares
            resumen = df_final.groupby("Estudiante")["Nota"].mean().round(2).reset_index()
            resumen.columns = ["Estudiante", "Promedio Recibido"]
            resumen["Factor (0-1)"] = (resumen["Promedio Recibido"] / 20).round(2)
            
            st.dataframe(resumen, use_container_width=True)
            
            st.write("### Detalle de todas las votaciones")
            st.dataframe(df_final)

            if st.button("Cerrar Sesión"):
                st.session_state.docente_auth = False
                st.rerun()
        else:
            st.info("Aún no hay datos registrados en el sistema.")





