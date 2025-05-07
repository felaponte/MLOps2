import streamlit as st
import requests

def prediction_page():
    st.title('Predicción de Cobertura Forestal')

    # Obtener la lista de modelos desde el API
    try:
        model_response = requests.get("http://api-service:8989/models")
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
    age = st.number_input('age', value=0.0)
    admission_type_id = st.number_input('admission_type_id', value=0.0)
    discharge_disposition_id = st.number_input('discharge_disposition_id', value=0.0)
    admission_source_id = st.number_input('admission_source_id', value=0.0)
    time_in_hospital = st.number_input('time_in_hospital', value=0.0)
    num_lab_procedures = st.number_input('num_lab_procedures', value=0.0)
    num_procedures = st.number_input('num_procedures', value=0.0)
    num_medications = st.number_input('num_medications', value=0.0)
    number_diagnoses = st.number_input('number_diagnoses', value=0.0)
    diabetesMed = st.number_input('diabetesMed', value=0.0)

    if st.button('¡Predecir!'):
        payload = {
            "age": age,
            "admission_type_id": admission_type_id,
            "discharge_disposition_id": discharge_disposition_id,
            "admission_source_id": admission_source_id,
            "time_in_hospital": time_in_hospital,
            "num_lab_procedures": num_lab_procedures,
            "num_procedures": num_procedures,
            "num_medications": num_medications,
            "number_diagnoses": number_diagnoses,
            "diabetesMed": diabetesMed
        }

        try:
            response = requests.post(
                f"http://api-service:8989/predict?modelo_elegir={selected_model}",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            st.success(f"Modelo usado: {result['modelo_usado']}, readmitted: {result['readmitted']}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error al conectarse con la API: {e}")
