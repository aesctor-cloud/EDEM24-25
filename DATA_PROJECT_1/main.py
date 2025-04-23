import streamlit as st
from data import get_data
from data import get_mapa
from data import ponderar

st.set_page_config(
    page_title="Encuentra tu barrio ideal",
    page_icon="🏡",
    layout="wide", 
    initial_sidebar_state="collapsed" 
)

# Traemos los datos
df_base = get_data()

# Título
st.title("Encuentra el mejor barrio para tu nueva vivienda")

col1, col2, col3 = st.columns([1.5,0.2,2])

with col1:
    st.write("#### Personaliza tu búsqueda:")
    st.write("Contesta las siguientes preguntas, siendo 0 'Nada importante' y 5 'Muy importante'")

    # Lista de los factores
    factores = ['el precio del alquiler', 'el precio de compra', 'las paradas de metro', 'las paradas de autobús','la tasa de vulnerabilidad','los hospitales cercanos','los parques infantiles cercanos']

    # Diccionario para respuestas formulario
    respuestas = {}

    # Formulario y recogida en diccionario
    with st.form(key="form", border=True):
        for factor in factores:
            respuestas[factor] = st.slider( # poniendo [factor] estamos indicando que es la key del diccionario
                f"¿Cómo de importante es para ti {factor}?", 
                0,5,0
                ) # la opción elegida es el valor del diccionario
        enviar = st.form_submit_button("Enviar preferencias")

with col2:
    st.write(" ")

with col3:
    
    # Creamos el mapa
    if enviar:
        st.write("#### Los mejores barrios según tus preferencias:")

        df_ponderado = ponderar(respuestas, df_base)

        top_barrios = df_ponderado.sort_values(by="valoración", ascending=False)['barrio'].iloc[:3].to_list()

        st.write("Los barrios que más se adaptan a lo que buscas son:")
        for i, barrio in enumerate(top_barrios, start=1):
            st.write(f"{i}. {barrio}")
        st.write("*Contesta de nuevo a las preguntas para ver otros resultados*")

        mapa = get_mapa(df_ponderado)
        st.plotly_chart(mapa, theme="streamlit", use_container_width=True)
    else:
        st.write(" ")