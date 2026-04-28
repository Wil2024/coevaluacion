import streamlit as st
import pandas as pd
import requests

# ==========================================
# CONFIGURACIÓN GENERAL Y BASE DE DATOS
# ==========================================
SHEETDB_API_URL = "https://sheetdb.io/api/v1/vehoumph81svs"
CLAVE_DOCENTE = "docentejwts123"

equipos_estudiantes = {
    "Equipo 1": ["Deans Cabrera", "Miguel Herrera", "Eleana Navio", "Deisy Salazar", "Gianfranco Vaccari"],
    "Equipo 2": ["Daniel Pinedo", "Jorge Acero", "Milagro Molina", "Sergio Valencia", "Yoseff Vilcapoma"],
    "Equipo 3": ["Andrés Álvarez", "Jacklyn Beraún", "Oscar Garnique", "Rafael Marca", "Nohelia Tang", "Jessica Timana"]
}

# --- FUNCIONES DE API ---
def guardar_evaluacion(datos):
    try:
        response = requests.post(SHEETDB_API_URL, json={"data": datos})
        return response.status_code in [200, 201]
    except:
        return False

# st.cache_data guarda los datos por 5 segundos para no agotar las peticiones a SheetDB
@st.cache_data(ttl=5)
def obtener_evaluaciones():
    try:
        response = requests.get(SHEETDB_API_URL)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return pd.DataFrame(data)
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# ==========================================
# INTERFAZ DE USUARIO
# ==========================================
st.set_page_config(page_title="Sistema de Coevaluación", page_icon="🎓", layout="centered")

st.title("🎓 Coevaluación - Business Intelligence & Business Analytics")
st.markdown("Plataforma segura para la evaluación de desempeño en equipos.")

modo = st.sidebar.radio("Navegación", ["👨‍🎓 Modo Estudiante", "👨‍🏫 Panel Docente"])

# ==========================================
# MODO ESTUDIANTE
# ==========================================
if modo == "👨‍🎓 Modo Estudiante":
    
    # 1. ESTADO DE ÉXITO Y BLOQUEO DE SESIÓN
    if st.session_state.get("evaluacion_completada", False):
        st.success("🎉 ¡Tu coevaluación se ha registrado de manera exitosa y segura!")
        st.balloons()
        st.info("🔒 La plataforma se ha bloqueado para tu usuario. Ya puedes cerrar esta ventana.")
        st.stop() # Detiene la ejecución del script aquí mismo para no mostrar más nada.

    # 2. IDENTIFICACIÓN
    st.subheader("Paso 1: Identificación")
    
    col1, col2 = st.columns(2)
    with col1:
        equipo_sel = st.selectbox("Selecciona tu equipo", ["Seleccionar..."] + list(equipos_estudiantes.keys()))
    
    if equipo_sel != "Seleccionar...":
        integrantes = equipos_estudiantes[equipo_sel]
        with col2:
            evaluador = st.selectbox("Selecciona tu nombre", ["Seleccionar..."] + integrantes)

        if evaluador != "Seleccionar...":
            
            # 3. VERIFICACIÓN EN BASE DE DATOS (ANTIDUPLICIDAD ESTRICTA)
            with st.spinner("Validando registros en el servidor..."):
                df_db = obtener_evaluaciones()
                obtener_evaluaciones.clear() # Limpiamos caché para tener el dato más fresco al verificar

            ya_voto = False
            if not df_db.empty and "Evaluador" in df_db.columns:
                if evaluador in df_db["Evaluador"].values:
                    ya_voto = True

            if ya_voto:
                st.error(f"🔒 ACCESO DENEGADO: El usuario **{evaluador}** ya envió sus calificaciones.")
                st.warning("El sistema solo permite un envío por estudiante para garantizar la integridad de los promedios.")
            else:
                # 4. FORMULARIO DE EVALUACIÓN (Solo aparece si NO ha votado)
                st.markdown("---")
                st.subheader(f"Paso 2: Calificación del {equipo_sel}")
                st.info("Desliza los marcadores para evaluar a cada integrante (escala 0-20).")
                
                # Usar st.form agrupa los datos y evita recargas indeseadas al mover los sliders
                with st.form("form_notas"):
                    notas = {}
                    for nombre in integrantes:
                        notas[nombre] = st.slider(f"🌟 Desempeño de {nombre}", min_value=0, max_value=20, value=0.5, step=0.5)
                    
                    st.markdown("*(Recuerda que debes evaluarte a ti mismo con honestidad)*")
                    
                    # Botón de envío nativo del formulario
                    submitted = st.form_submit_button("🚀 Enviar Calificaciones Oficiales", use_container_width=True)

                    if submitted:
                        with st.spinner("Guardando datos de forma segura..."):
                            paquete_datos = []
                            for est, nota in notas.items():
                                paquete_datos.append({
                                    "Equipo": equipo_sel,
                                    "Estudiante": est,
                                    "Evaluador": evaluador,
                                    "Nota": nota,
                                    "Fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M") # Añadimos registro de tiempo
                                })
                            
                            if guardar_evaluacion(paquete_datos):
                                # Cambiamos el estado y forzamos recarga hacia la pantalla de éxito definitiva
                                st.session_state.evaluacion_completada = True
                                st.rerun()
                            else:
                                st.error("⚠️ Error de conexión con el servidor. Por favor, intenta de nuevo.")

# ==========================================
# MODO DOCENTE (DASHBOARD)
# ==========================================
elif modo == "👨‍🏫 Panel Docente":
    st.subheader("🔐 Portal de Administración")
    
    if not st.session_state.get("acceso_concedido", False):
        clave = st.text_input("Contraseña Maestra", type="password")
        if st.button("Acceder al Dashboard"):
            if clave == CLAVE_DOCENTE:
                st.session_state.acceso_concedido = True
                st.rerun()
            else:
                st.error("Clave incorrecta")
    else:
        # Obtener datos de la base
        df_completo = obtener_evaluaciones()
        
        # Botón para cerrar sesión alineado a la derecha
        col_cerrar1, col_cerrar2 = st.columns([0.8, 0.2])
        with col_cerrar2:
            if st.button("Cerrar Sesión", use_container_width=True):
                st.session_state.acceso_concedido = False
                st.rerun()

        if not df_completo.empty:
            df_completo["Nota"] = pd.to_numeric(df_completo["Nota"], errors='coerce')
            total_votos = df_completo["Evaluador"].nunique()
            
            # Tarjetas de métricas visuales
            st.markdown("### 📈 Resumen en Tiempo Real")
            m1, m2, m3 = st.columns(3)
            m1.metric("Estudiantes que han votado", f"{total_votos}")
            m2.metric("Total de calificaciones", len(df_completo))
            m3.metric("Promedio Global", f'{df_completo["Nota"].mean():.2f}')
            
            # Pestañas organizativas para no saturar la pantalla
            tab1, tab2 = st.tabs(["📊 Promedios y Factores", "📋 Registro Bruto (Auditoría)"])
            
            with tab1:
                resumen = df_completo.groupby(["Equipo", "Estudiante"])["Nota"].mean().round(2).reset_index()
                resumen.columns = ["Equipo", "Estudiante", "Promedio Recibido"]
                resumen["Factor de Ajuste (0-1)"] = (resumen["Promedio Recibido"] / 20).round(2)
                st.dataframe(resumen, use_container_width=True, hide_index=True)
                
            with tab2:
                st.dataframe(df_completo, use_container_width=True, hide_index=True)
                
        else:
            st.info("Aún no hay respuestas registradas en la base de datos.")
