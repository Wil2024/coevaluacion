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

# Configuración visual
st.set_page_config(page_title="Sistema de Coevaluación", page_icon="🎓")
st.title("🎓 Aplicación de Coevaluación Grupal")

modo = st.sidebar.selectbox("Seleccione modo", ["Estudiante", "Docente"])

if modo == "Estudiante":
    st.header("📝 Formulario de Coevaluación")

    # 1. Selección de datos básicos
    equipo_sel = st.selectbox("Selecciona tu equipo", options=["Seleccionar..."] + list(equipos_estudiantes.keys()))
    
    if equipo_sel != "Seleccionar...":
        integrantes = equipos_estudiantes[equipo_sel]
        evaluador = st.selectbox("Tu Nombre (Evaluador)", options=["Seleccionar..."] + integrantes)

        if evaluador != "Seleccionar...":
            # --- BLOQUEO PERSISTENTE: Verificación en la Base de Datos ---
            with st.spinner("Verificando registros previos..."):
                df_historico = obtener_evaluaciones()
            
            ya_realizo_envio = False
            if not df_historico.empty and "Evaluador" in df_historico.columns:
                # Comprobamos si el nombre seleccionado ya envió datos anteriormente
                if evaluador in df_historico["Evaluador"].values:
                    ya_realizo_envio = True

            # 2. Lógica de visualización condicionada a la base de datos
            if ya_realizo_envio:
                st.error(f"🚫 Lo sentimos, {evaluador}. Ya has registrado tu coevaluación anteriormente.")
                st.info("Para evitar duplicados, el sistema no permite múltiples envíos por persona.")
                st.balloons() # Mantener globos si acaba de enviar
            else:
                # El formulario solo aparece si NO hay registros en la base de datos
                st.write("---")
                st.write(f"### Califica a tus compañeros de {equipo_sel}:")
                
                notas = {}
                for nombre in integrantes:
                    notas[nombre] = st.slider(f"Nota para {nombre}", 0.0, 20.0, 10.0, 0.5, key=f"s_{nombre}")

                if st.button("🚀 Enviar Evaluación"):
                    datos_finales = []
                    for estudiante, nota in notas.items():
                        datos_finales.append({
                            "Equipo": equipo_sel,
                            "Estudiante": estudiante,
                            "Evaluador": evaluador,
                            "Nota": nota
                        })
                    
                    if guardar_evaluacion(datos_finales):
                        st.success("✅ ¡Enviado con éxito!")
                        # Al recargar, la validación de arriba detectará el nombre en la API y bloqueará el botón
                        st.rerun()
                    else:
                        st.error("Error al conectar con la base de datos.")

elif modo == "Docente":
    st.header("🔐 Acceso Docente")
    if "docente_ok" not in st.session_state:
        st.session_state.docente_ok = False

    if not st.session_state.docente_ok:
        clave = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if clave == CLAVE_DOCENTE:
                st.session_state.docente_ok = True
                st.rerun()
            else:
                st.error("Clave incorrecta")
    else:
        df_docente = obtener_evaluaciones()
        if not df_docente.empty:
            df_docente["Nota"] = pd.to_numeric(df_docente["Nota"], errors='coerce')
            st.subheader("Resultados Consolidados")
            
            # Promedios recibidos por cada alumno
            resumen = df_docente.groupby("Estudiante")["Nota"].mean().round(2).reset_index()
            resumen["Factor"] = (resumen["Nota"] / 20).round(2)
            st.table(resumen)
            
            st.write("#### Detalle Completo")
            st.dataframe(df_docente)
            
            if st.button("Cerrar Sesión"):
                st.session_state.docente_ok = False
                st.rerun()
        else:
            st.info("No hay datos.")
