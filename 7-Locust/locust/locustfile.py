from locust import HttpUser, task, between

class UsuarioDeCarga(HttpUser):
    wait_time = between(1, 2.5)

    @task
    def hacer_inferencia(self):
        payload = {
                "Elevation": 0,
                "Aspect": 0,
                "Slope": 0,
                "Horizontal_Distance_To_Hydrology": 0,
                "Vertical_Distance_To_Hydrology": 0,
                "Horizontal_Distance_To_Roadways": 0,
                "Hillshade_9am": 0,
                "Hillshade_Noon": 0,
                "Hillshade_3pm": 0,
                "Horizontal_Distance_To_Fire_Points": 0
        }
        # Enviar una petición POST al endpoint /predict
        response = self.client.post("/predict?modelo_elegir=best_gradient_boosting", json=payload)
        # Opcional: validación de respuesta
        if response.status_code != 200:
            print("❌ Error en la inferencia:", response.text)
