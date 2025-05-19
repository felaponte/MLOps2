=======
# Taller: CI/CD y GitOps para despliegue de API de IA

## Objetivo del Taller

Diseñar e implementar una arquitectura **CI/CD con GitOps** para desplegar una API FastAPI con un modelo de IA, incluyendo observabilidad con **Prometheus** y **Grafana**, utilizando **GitHub Actions**, **Docker**, **Kubernetes** y **Argo CD**.

---
## Estructura del Proyecto

```
10-CI_CD/
├── api/
│ ├── app/                            # Código de la API FastAPI
│ │ ├── Dockerfile
│ │ ├── main.py
│ │ ├── model.pkl
│ │ └── requirements.txt
│ ├── train_model.py                  # Entrena y guarda model.pkl
│ ├── penguins_lter.csv               # Dataset
├── loadtester/                       # Script que hace carga a la API
│ ├── Dockerfile
│ ├── main.py
│ └── requirements.txt
├── manifests/                        # Manifiestos K8s para API, Loadtester, Prometheus y Grafana
│ ├── api-deployment.yaml
│ ├── api-service.yaml
│ ├── grafana-dashboard-api.yaml
│ ├── grafana-dashboards-config.yaml
│ ├── grafana-datasources.yaml 
│ ├── grafana-deployment.yaml 
│ ├── grafana-service.yaml 
│ ├── kustomization.yaml
│ ├── loadtester-deployment.yaml
│ ├── prometheus-configmap.yaml
│ ├── prometheus-deployment.yaml
│ └── prometheus-service.yaml 
├── argo-cd/                          # Configuración de Argo CD
│ ├── install-argocd.yaml
│ └── app.yaml
└── docker-compose.yaml               # (opcional para entorno local)
├── readme.md
```
---
## Componentes Implementados

* FastAPI: expone un endpoint `/predict` que utiliza `model.pkl` y otro `/metrics` con `prometheus_client`.

* LoadTester: envía peticiones periódicas al endpoint `/predict`.

* Prometheus: scrapea métricas desde `/metrics`.

* Grafana: visualiza métricas en dashboards configurados.

* GitHub Actions: entrena el modelo, construye y publica imágenes Docker con tags como `v009`.

* Argo CD: sincroniza automáticamente los manifiestos desde GitHub y actualiza el clúster de Kubernetes.
---

## Despliegue y Uso

### Requisitos

- Kubernetes (en este caso se usó `microk8s`)
- Docker
- GitHub con acceso a Actions
- ArgoCD configurado y accesible (puerto 8080)

### 1. Entrenar el modelo

- `GitHub Actions` entrena automáticamente el modelo desde el archivo `train_model.py` y guarda el archivo `model.pkl`.
- `Argo CD` sincroniza automáticamente los manifiestos Kubernetes desde GitHub.

### 2. Construir y subir imágenes Docker

Corre localmente o por GitHub Actions:

```
git tag v010
git push origin v010
```
Esto genera nuevas imágenes, y ArgoCD sincroniza automáticamente los cambios (gracias al kustomization.yaml).

### 3. Acceder a ArgoCD

```
sudo microk8s kubectl port-forward svc/argocd-server -n argocd 8080:443
```

- URL: http://localhost:8080
- Usuario: admin
- Contraseña (obtenida con):

```
sudo microk8s kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 --decode && echo
```

### 4. Visualizar Grafana

```
sudo microk8s kubectl port-forward svc/grafana -n default 3000:3000
```
- Accede en: http://localhost:3000
- Dashboard muestra el tráfico generado por loadtester.

### Endpoints de la API

Se implementa una API con:

- `POST /predict` para inferencia usando el modelo entrenado.
- `GET /metrics` para exponer métricas de Prometheus.
- `GET /` como endpoint de prueba.


### Manifiestos Kubernetes

Incluyen:
- api-deployment.yaml y api-service.yaml
- loadtester-deployment.yaml
- prometheus-deployment.yaml, prometheus-configmap.yaml
- grafana-deployment.yaml, grafana-datasources.yaml, grafana-dashboards-config.yaml
- kustomization.yaml para automatizar despliegue vía Argo CD

### Observabilidad

- El endpoint /metrics es recogido por Prometheus automáticamente.
- Dashboards de Grafana ya configurados para observar el tráfico generado por loadtester.
- Usa kubectl port-forward para ver Grafana localmente:

```
sudo microk8s kubectl port-forward svc/grafana -n default 3000:3000
```
Luego ingresa en: http://localhost:3000

### Evaluación del Taller

| Criterio                            | Evidencia                                                 |
| ----------------------------------- | --------------------------------------------------------- |
| Estructura y manifiestos YAML (20%) | Carpeta `manifests/` con todos los archivos requeridos    |
| Dockerfiles funcionales (15%)       | En `api/` y `loadtester/`                                 |
| Entrenamiento automatizado (15%)    | En pipeline de GitHub Actions (`train_model.py`)          |
| Métricas Prometheus (20%)           | Endpoint `/metrics` + configuración en `prometheus.yml`   |
| Visualización en Grafana (10%)      | Dashboards y forwarding configurado                       |
| GitHub Actions + Argo CD (20%)      | `ci-cd.yml`, tagging (`v009`), `kustomization.yaml`, sync |

### Evidencia visual de Despliegue CI/CD

A continuación se presentan capturas que validan la ejecución exitosa del pipeline y la sincronización con ArgoCD.

#### Ejecución del pipeline CI/CD en GitHub Actions
![Pipeline GitHub Actions](./imagenes/pipeline_success.jpeg)

### Sincronización automática en Argo CD

![Sincronización Argo CD](./imagenes/argocd_sync.jpeg)