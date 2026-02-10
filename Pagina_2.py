import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# Configuración de página
st.set_page_config(page_title="Calendario Depto Playa", page_icon="🏖️", layout="centered")

st.title("🏖️ Reserva Depto Familiar")
st.markdown("Registra tus fechas para que el resto de los hermanos sepa cuándo estará ocupado.")

# 1. Conexión con Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0) 
except Exception as e:
    st.error("Error de conexión. Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# 2. Formulario de Reserva en la barra lateral
with st.sidebar:
    st.header("Nueva Reserva")
    with st.form("reserva_form"):
        nombre = st.selectbox("¿Quién reserva?", ["Lukas", "JP", "Paula", "Tomas"]) 
        
        # Calendario de Rango Único (Corrige el error de fechas duplicadas)
        fechas = st.date_input(
            "Selecciona periodo (Entrada y Salida)",
            value=(date.today(), date.today()),
            min_value=date.today()
        )
        
        submit = st.form_submit_button("Confirmar Reserva")

    if submit:
        # Validar que el usuario seleccionó un rango (inicio y fin)
        if isinstance(fechas, tuple) and len(fechas) == 2:
            fecha_inicio, fecha_fin = fechas
            
            # Preparar DataFrame para comparación
            df['Inicio'] = pd.to_datetime(df['Inicio']).dt.date
            df['Fin'] = pd.to_datetime(df['Fin']).dt.date
            
            # Lógica de validación de traslapes (overlapping)
            conflicto = df[
                ((fecha_inicio >= df['Inicio']) & (fecha_inicio <= df['Fin'])) |
                ((fecha_fin >= df['Inicio']) & (fecha_fin <= df['Fin'])) |
                ((fecha_inicio <= df['Inicio']) & (fecha_fin >= df['Fin']))
            ]

            if not conflicto.empty:
                st.error(f"❌ ¡Error! Esas fechas ya están tomadas por {conflicto['Hermano'].values[0]}.")
            else:
                nueva_reserva = pd.DataFrame([{
                    "Hermano": nombre,
                    "Inicio": str(fecha_inicio),
                    "Fin": str(fecha_fin)
                }])
                
                try:
                    # Guardar fila en el Excel
                    conn.create(worksheet="Sheet1", data=nueva_reserva)
                    st.success("✅ ¡Reserva guardada con éxito!")
                    st.balloons()
                    st.rerun() 
                except Exception as e:
                    st.error(f"Hubo un problema al guardar: {e}")
        else:
            st.warning("⚠️ Por favor, selecciona la fecha de llegada y LUEGO la de salida en el calendario.")

# 3. Mostrar el Calendario
st.subheader("🗓️ Calendario de Ocupación")

if not df.empty:
    df_sorted = df.sort_values(by="Inicio")
    st.table(df_sorted)
else:
    st.info("Aún no hay reservas. ¡Sé el primero!")

st.info("💡 Consejo: Revisa el calendario antes de pedir fechas en el grupo de WhatsApp.")