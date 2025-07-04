import streamlit as st
from data_utils import load_data, check_dataset_freshness

st.set_page_config(
    page_title="Chimpanzee Behavior Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Bienvenido al Chimpanzee Behavior Dashboard")

st.markdown(
    """
Esta aplicación te permite explorar de forma interactiva los datos de comportamiento de los chimpancés.

Desde el menú lateral puedes acceder a:

- **history**: observar la evolución temporal de una conducta.
- **snapshot**: revisar la distribución de comportamientos en un periodo concreto.
- **comparison**: comparar distintos filtros o periodos de tiempo.

Utiliza las herramientas de cada página para filtrar la información y, si lo necesitas, descargar los resultados obtenidos.
"""
)

df = load_data()
if not df.empty:
    check_dataset_freshness(df)
else:
    st.error(
        "No se encontró un archivo de datos válido. Sube un CSV cuando se solicite en las otras páginas para comenzar."
    )
