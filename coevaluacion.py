import streamlit as st
import pandas as pd
import requests

# === CONFIGURACIÓN ===
# URL de SheetDB para la conexión con Excel
SHEETDB_API_URL = "https://sheetdb.io/api/v1/vehoumph81svs"
CLAVE_DOCENTE = "docentejwts123"

# Listado de equipos y estudiantes
equipos_estudiantes = {
    "Equipo 1": ["Deans Cabrera", "Miguel Herrera", "Eleana Navio", "Deisy Salazar", "Gianfranco Vaccari"],
    "Equipo 2": ["Daniel Pinedo", "Jorge Acero", "Milagro Molina", "Sergio Valencia", "Yoseff Vilcapoma"],
    "Equipo 3": ["Andrés Álvarez", "Jacklyn Beraún", "Oscar Garnique", "Rafael Marca", "Nohelia Tang", "Jessica Timana"]
}

def guardar_evaluacion(datos):
    """Envía los datos a SheetDB"""
    payload = {"data": datos}
    response = requests.post(SHEETDB_API_URL, json=payload)
    return response.status_code == 201 or response.status_code == 200

def obtener_evaluaciones():
    """Obtiene los datos desde SheetDB"""
    try:
        response = requests.get(SHEETDB_API_URL)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# Configuración de la página
st.set_page_config(page_title="Sistema de Coevaluación", page_icon="🎓")
st.title("🎓 Aplicación de Coevaluación Grupal")

# Selector de modo en la barra lateral
modo = st.sidebar.selectbox("Seleccione modo", ["Estudiante", "Docente"])

if modo == "Estudiante":
    st.header("📝 Formulario de Coevaluación")

    # 1. Inicializar el estado de envío para que el botón pueda desaparecer
    if "evaluacion_enviada" not in st.session_state:
        st.session_state.evaluacion_enviada = False

    # 2. Lógica de control: Si ya envió, mostramos éxito; si no, mostramos el formulario
    if st.session_state.evaluacion_enviada:
        st.success("✅ Evaluación enviada correctamente. Tus respuestas han sido registradas.")
        st.balloons()  # Burbujas de colores de éxito
        st.info("Ya no puedes realizar más envíos en esta sesión para evitar duplicados.")
    else:
        equipo_seleccionado = st.selectbox("Selecciona tu equipo", options=["Seleccionar..."] + list(equipos_estudiantes.keys()))

        if equipo_seleccionado != "Seleccionar...":
            integrantes = equipos_estudiantes[equipo_seleccionado]
            evaluador = st.selectbox("Tu Nombre (Quien evalúa)", options=["Seleccionar..."] + integrantes)

            if evaluador != "Seleccionar...":
                st.write("---")
                st.write(f"### Califica a cada compañero de {equipo_seleccionado}:")
                
                notas = {}
                for nombre in integrantes:
                    # Slider para cada integrante
                    nota = st.slider(f"Nota para {nombre}", min_value=0.0, max_value=20.0, step=0.5, key=f"nota_{nombre}")
                    notas[nombre] = nota

                # EL BOTÓN: Desaparecerá después de ejecutarse con éxito
                if st.button("🚀 Enviar Evaluación"):
                    # Preparar los datos para enviar
                    datos_lista = []
                    for estudiante, nota in notas.items():
                        datos_lista.append({
                            "Equipo": equipo_seleccionado,
                            "Estudiante": estudiante,
                            "Evaluador": evaluador,
                            "Nota": nota
                        })
                    
                    # Intentar el guardado
                    with st.spinner("Guardando en la base de datos..."):
                        if guardar_evaluacion(datos_lista):
                            # Cambiamos el estado a True para que el botón desaparezca al recargar
                            st.session_state.evaluacion_enviada = True
                            st.rerun()  # Recarga el script con el nuevo estado
                        else:
                            st.error("Hubo un error al enviar los datos. Inténtalo de nuevo.")

elif modo == "Docente":
    st.header("🔐 Acceso al Modo Docente")
    
    if "auth_docente" not in st.session_state:
        st.session_state.auth_docente = False

    if not st.session_state.auth_docente:
        clave_input = st.text_input("Ingrese la contraseña del docente", type="password")
        if st.button("Ingresar"):
            if clave_input == CLAVE_DOCENTE:
                st.session_state.auth_docente = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    else:
        st.success("🔓 Acceso concedido.")
        
        # Obtener datos reales desde la API
        df = obtener_evaluaciones()

        if df.empty:
            st.info("No hay evaluaciones registradas aún.")
        else:
            st.subheader("Reporte de Notas")
            # Convertir columna Nota a número para cálculos
            df["Nota"] = pd.to_numeric(df["Nota"], errors='coerce')
            
            # Tabla completa
            st.write("#### Detalle General")
            st.dataframe(df)

            # Promedio por Estudiante
            st.write("#### Promedios y Factor de Ajuste")
            promedios = df.groupby("Estudiante")["Nota"].mean().round(2).reset_index()
            promedios["Factor Ajuste"] = (promedios["Nota"] / 20).round(2)
            st.dataframe(promedios)

            if st.button("Cerrar Sesión"):
                st.session_state.auth_docente = False
                st.rerun()



