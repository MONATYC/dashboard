import streamlit as st

st.set_page_config(
    page_title="Home",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    st.title("Bienvenido al Dashboard de Comportamiento de Chimpancés")
    st.write(
        """
        Esta aplicación te permite explorar de forma interactiva la base de datos
        comportamentales recopilada por nuestro equipo. Desde aquí podrás:
        • Consultar la historia de cada conducta en la sección *history*.
        • Analizar un periodo concreto usando *snapshot*.
        • Comparar distintos filtros y fechas en *comparison*.

        Utiliza el menú lateral para navegar por las funcionalidades.
        """
    )

if __name__ == "__main__":
    main()
