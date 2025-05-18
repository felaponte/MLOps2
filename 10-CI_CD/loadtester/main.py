import time
import random
import requests

# URL base del contenedor de la API (usando el nombre del servicio en docker-compose)
BASE_URL = "http://api:8989"

# Generador de datos aleatorios válidos para el modelo
def generar_datos():
    return {
        "Culmen_Length_mm": round(random.uniform(30.0, 60.0), 2),
        "Culmen_Depth_mm": round(random.uniform(13.0, 21.0), 2),
        "Flipper_Length_mm": round(random.uniform(170.0, 230.0), 2),
    }

def load_test():
    while True:
        try:
            # Escoge entre / y /predict aleatoriamente
            if random.random() < 0.2:
                r = requests.get(f"{BASE_URL}/")
                print(f"GET / -> {r.status_code}")
            else:
                datos = generar_datos()
                r = requests.post(f"{BASE_URL}/predict", json=datos)
                print(f"POST /predict {datos} -> {r.status_code} - {r.json() if r.ok else r.text}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    load_test()