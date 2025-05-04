from locust import HttpUser, task, between

class UsuarioDeCarga(HttpUser):
    # Tiempo de espera entre tareas por usuario simulado (en segundos)
    wait_time = between(1, 2.5)

    @task
    def hacer_inferencia(self):
        payload = {
            "Elevation": 1,
            "Aspect": 1,
            "Slope": 1,
            "Horizontal_Distance_To_Hydrology": 1,
            "Vertical_Distance_To_Hydrology": 1,
            "Horizontal_Distance_To_Roadways": 1,
            "Hillshade_9am": 1,
            "Hillshade_Noon": 1,
            "Hillshade_3pm": 1,
            "Horizontal_Distance_To_Fire_Points": 1

        }
        # Enviar una petición POST al endpoint /predict
        response = self.client.post("/predict?modelo_elegir=best_gb", json=payload)
        # Opcional: validación de respuesta
        if response.status_code != 200:
            print("❌ Error en la inferencia:", response.text)
