import streamlit as st
import requests

def prediction_page():
    st.title('Predicción de Cobertura Forestal')

    # Obtener la lista de modelos desde el API
    try:
        model_response = requests.get("http://api_service:8989/models")
        model_response.raise_for_status()
        models = model_response.json().get("models", [])
    except Exception as e:
        st.error(f"Error al obtener modelos del API: {e}")
        return

    if not models:
        st.warning("No hay modelos registrados disponibles en MLflow.")
        return

    # Input para escoger modelo
    selected_model = st.selectbox("Selecciona un modelo", models)

    # Inputs para el usuario
    elevation = st.number_input('Elevación', value=2500.0)
    aspect = st.number_input('Orientación (Aspect)', value=45.0)
    slope = st.number_input('Pendiente (Slope)', value=10.0)
    horizontal_hydro = st.number_input('Distancia Horizontal a Hidrología', value=120.0)
    vertical_hydro = st.number_input('Distancia Vertical a Hidrología', value=20.0)
    horizontal_road = st.number_input('Distancia Horizontal a Carreteras', value=300.0)
    hillshade_9am = st.number_input('Sombras a las 9am', value=220.0)
    hillshade_noon = st.number_input('Sombras al mediodía', value=230.0)
    hillshade_3pm = st.number_input('Sombras a las 3pm', value=180.0)
    horizontal_fire = st.number_input('Distancia Horizontal a Puntos de Incendio', value=400.0)

    if st.button('¡Predecir!'):
        payload = {
            "Elevation": elevation,
            "Aspect": aspect,
            "Slope": slope,
            "Horizontal_Distance_To_Hydrology": horizontal_hydro,
            "Vertical_Distance_To_Hydrology": vertical_hydro,
            "Horizontal_Distance_To_Roadways": horizontal_road,
            "Hillshade_9am": hillshade_9am,
            "Hillshade_Noon": hillshade_noon,
            "Hillshade_3pm": hillshade_3pm,
            "Horizontal_Distance_To_Fire_Points": horizontal_fire
        }

        try:
            response = requests.post(
                f"http://api_service:8989/predict?modelo_elegir={selected_model}",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            st.success(f"Modelo usado: {result['modelo usado']}, Cover Type: {result['Cover_Type']}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error al conectarse con la API: {e}")
