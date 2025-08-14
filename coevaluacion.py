import streamlit as st
import pandas as pd
import requests

# === CAMBIA SOLO ESTA LÍNEA CON TU URL DE SHEETDB.IO ===
SHEETDB_API_URL = "https://sheetdb.io/api/v1/vehoumph81svs"  # ← Sin espacio al final

CLAVE_DOCENTE = "docentejwts123"

equipos_estudiantes = {
    "Equipo 1": ["Selecciona tu nombre","ALVAREZ NUÑEZ CINTHYA LIZETH", "CASTILLO ESPINOZA JUAN EMILIO", "CUZCANO ROJAS JHONNY JOSE","GUEVARA AMARILLO JASMIN FABIOLA","ROBLES VICTORIA PAMELA KARLA"],
    "Equipo 2": ["Selecciona tu nombre", "CALIXTO VILLACORTA JONNATHAN","SANTANA YANA SAMUEL JOSE","GONZALES CHAFLOQUE LEYLA JENNIFER", "GONZALES RODRIGUEZ ERIKA VANESSA", "CASTRO BALBOA HEYDA ADELAIDA"],
    "Equipo 3": ["Selecciona tu nombre", "TEJADA CABREJOS FERNANDO", "OSORIO ANYOZA	 RENZO ESTEBAN", "NUÑEZ SANCHO LUIYE ESTHIP", "MOYA CONTRERAS GULIANNA"],
    "Equipo 4": ["Selecciona tu nombre","Davila Torres Karen", "Sempertegui Flores Natali", "Tarazona Montero Luis","Vivas Gonzales Samby"],
    "Equipo 5": ["Selecciona tu nombre","Ramos Quispe 	Humberto Erick", "Panca Velasquez Kelly Susan", "Gamboa Espinoza Edwin Manuel","Zamora Quispe Gaby Daniela"]
}

def guardar_evaluacion(datos):
    payload = {"data": datos}
    response = requests.post(SHEETDB_API_URL, json=payload)
    if response.status_code not in [200, 201]:
        st.error(f"🚫 Error técnico: {response.text}")
        return False
    return True

def obtener_evaluaciones():
    response = requests.get(SHEETDB_API_URL)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("❌ No se pudo cargar desde SheetDB.")
        return pd.DataFrame()

st.title("🎓 Aplicación de Coevaluación Grupal")

modo = st.sidebar.selectbox("Seleccione modo", ["Estudiante", "Docente"])

if modo == "Estudiante":
    st.header("📝 Formulario de Coevaluación")

    equipo_seleccionado = st.selectbox("Selecciona tu equipo", options=list(equipos_estudiantes.keys()))

    if equipo_seleccionado:
        integrantes = equipos_estudiantes[equipo_seleccionado]
        evaluador = st.selectbox("Selecciona tu nombre:", options=integrantes)

        st.write("### Califica a cada compañero de tu equipo (incluyéndote):")
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
                if guardar_evaluacion(datos):
                    st.success("✅ Evaluación enviada correctamente.")
                else:
                    st.warning("⚠️ Hubo un problema al enviar los datos.")

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

        df = obtener_evaluaciones()

        if df.empty:
            st.info("No hay evaluaciones registradas aún.")
        else:
            st.subheader("Todas las Evaluaciones")
            st.dataframe(df)

            st.subheader("Promedio por Estudiante")

            # Convertir 'Nota' a tipo numérico (por si viene como string)
            df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce')

            # Calcular promedio
            promedios = df.groupby("Estudiante")["Nota"].mean().round(2).reset_index()
            promedios.rename(columns={"Nota": "Nota Promedio"}, inplace=True)

            # Factor de ajuste
            promedios["Factor Ajuste"] = (promedios["Nota Promedio"] / 20).round(2)

            st.dataframe(promedios)

            st.download_button(
                label="📥 Descargar datos como CSV",
                data=promedios.to_csv(index=False),
                file_name="promedios_coevaluacion.csv",
                mime="text/csv"
            )

            if st.button("Cerrar Sesión"):
                st.session_state["acceso_docente"] = False
                st.experimental_rerun()
    else:
        st.info("Esperando contraseña...")








