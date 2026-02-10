import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# Configuración de página
st.set_page_config(page_title="Calendario Depto Playa", page_icon="🏖️", layout="centered")

st.title("🏖️ Reserva Depto Familiar")
st.markdown("Registra tus fechas para que el resto de los hermanos sepa cuándo estará ocupado.")

# 1. Conexión con Google Sheets
# Nota: La URL se configura luego en Streamlit Cloud o en un archivo local
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0) # ttl=0 para leer datos frescos siempre
except:
    st.error("Error de conexión. Asegúrate de configurar la URL del Google Sheet.")
    st.stop()

# 2. Formulario de Reserva en la barra lateral
with st.sidebar:
    st.header("Nueva Reserva")
    with st.form("reserva_form"):
        nombre = st.selectbox("¿Quién reserva?", ["Lukas", "JP", "Paula", "Tomas"]) # Cambia por tus nombres
        fecha_inicio = st.date_input("Fecha de llegada", min_value=date.today())
        fecha_fin = st.date_input("Fecha de salida", min_value=fecha_inicio)
        
        submit = st.form_submit_button("Confirmar Reserva")

    if submit:
        # Lógica para evitar traslapes (overlapping)
        df['Inicio'] = pd.to_datetime(df['Inicio']).dt.date
        df['Fin'] = pd.to_datetime(df['Fin']).dt.date
        
        conflicto = df[
            ((fecha_inicio >= df['Inicio']) & (fecha_inicio <= df['Fin'])) |
            ((fecha_fin >= df['Inicio']) & (fecha_fin <= df['Fin'])) |
            ((fecha_inicio <= df['Inicio']) & (fecha_fin >= df['Fin']))
        ]

        if not conflicto.empty:
            st.error(f"❌ ¡Error! Esas fechas ya están tomadas por {conflicto['Hermano'].values[0]}.")
        else:
            # Crear nueva fila
            nueva_reserva = pd.DataFrame([{
                "Hermano": nombre,
                "Inicio": str(fecha_inicio),
                "Fin": str(fecha_fin)
            }])
            
            # Actualizar Google Sheets
            updated_df = pd.concat([df, nueva_reserva], ignore_index=True)
            conn.update(data=updated_df)
            
            st.success("✅ ¡Reserva guardada con éxito!")
            st.balloons()
            st.rerun()

# 3. Mostrar el Calendario
st.subheader("🗓️ Calendario de Ocupación")

if not df.empty:
    # Ordenar por fecha de inicio
    df_sorted = df.sort_values(by="Inicio")
    
    # Mostrar tabla limpia
    st.table(df_sorted)
else:
    st.info("Aún no hay reservas. ¡Sé el primero!")

st.info("💡 Consejo: Revisa el calendario antes de pedir fechas en el grupo de WhatsApp.")