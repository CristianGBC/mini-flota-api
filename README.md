# Mini-Flota API

API REST para gestionar vehículos, conductores y la asignación de conductores a vehículos.

El proyecto fue desarrollado con FastAPI, MongoDB y autenticación mediante JWT. La aplicación mantiene separadas las responsabilidades de endpoints, validaciones y acceso a la base de datos.

## Tecnologías utilizadas

* Python
* FastAPI
* MongoDB
* Motor
* Pydantic v2
* JWT
* Passlib y bcrypt
* Poetry
* pytest
* pytest-asyncio

## Funcionalidades

* Comprobación del estado de la API.
* Inicio de sesión con JWT.
* Protección de rutas mediante token.
* Crear, listar, consultar, actualizar y eliminar vehículos.
* Crear y listar conductores.
* Asignar o cambiar el conductor de un vehículo.
* Validación de placas, años, capacidad y licencias.
* Control de placas y licencias duplicadas.
* Restricción para que un conductor no pueda estar asignado a dos vehículos.
* Pruebas unitarias con mocks, sin depender de una base de datos real.

## Arquitectura

La aplicación sigue la siguiente separación:

```text
Endpoint → Servicio → MongoDB
```

Los endpoints reciben y responden solicitudes HTTP, mientras que los servicios contienen la lógica de negocio y las operaciones con MongoDB.

```text
app/
├── api/
│   └── v1/
│       └── endpoints/
│           ├── auth.py
│           ├── drivers.py
│           └── vehicles.py
├── core/
│   └── security.py
├── schemas/
│   ├── driver.py
│   └── vehicle.py
├── services/
│   ├── driver_service.py
│   └── vehicle_service.py
├── config.py
├── database.py
└── main.py
```

## Requisitos

Antes de ejecutar el proyecto necesitas:

* Python instalado.
* Poetry instalado.
* MongoDB local, MongoDB Atlas o un contenedor Docker con MongoDB.
* Git.

## Instalación

Clona el repositorio:

```bash
git clone https://github.com/CristianGBC/mini-flota-api
cd mini-flota-api
```

Instala las dependencias:

```bash
poetry install
```

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=mini_flota
SECRET_KEY=coloca_aqui_una_clave_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

No subas el archivo `.env` al repositorio.

La variable `SECRET_KEY` debe contener un valor seguro y diferente en cada entorno.

## Ejecutar MongoDB con Docker

Puedes levantar una instancia local de MongoDB con:

```bash
docker run -d \
    --name mini-flota-mongo \
    -p 27017:27017 \
    mongo
```

Para comprobar que el contenedor está activo:

```bash
docker ps
```

## Ejecutar la API

Inicia el servidor:

```bash
poetry run uvicorn app.main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

La documentación Swagger estará disponible en:

```text
http://127.0.0.1:8000/docs
```

## Autenticación

La aplicación utiliza JWT.

El usuario envía sus credenciales al endpoint:

```text
POST /auth/login
```

Si las credenciales son correctas, la API devuelve:

```json
{
    "access_token": "TOKEN_JWT",
    "token_type": "bearer"
}
```

Las rutas protegidas necesitan el header:

```http
Authorization: Bearer TOKEN_JWT
```

Desde Swagger se puede ingresar el token mediante el botón **Authorize**.

## Endpoints principales

### Estado de la API

```text
GET /health
```

Respuesta:

```json
{
    "status": "ok"
}
```

### Autenticación

```text
POST /auth/login
```

### Vehículos

```text
POST   /vehicles/
GET    /vehicles/
GET    /vehicles/{vehicle_id}
PUT    /vehicles/{vehicle_id}
DELETE /vehicles/{vehicle_id}
```

### Conductores

```text
POST /drivers/
GET  /drivers/
```

### Asignar conductor

```text
PUT /vehicles/{vehicle_id}/driver
```

Body:

```json
{
    "driver_id": "ID_DEL_CONDUCTOR"
}
```

## Modelo de vehículo

```json
{
    "plate": "PDA-1234",
    "brand": "Toyota",
    "model": "Hilux",
    "year": 2024,
    "capacity_kg": 1000,
    "status": "active"
}
```

Reglas:

* La placa debe tener el formato `AAA-1234`.
* El año debe estar entre 1990 y el año actual.
* La capacidad debe ser mayor que cero.
* El estado debe ser `active` o `inactive`.
* La placa debe ser única.

## Modelo de conductor

```json
{
    "name": "Cristian Ca",
    "license": "1234567898"
}
```

Reglas:

* El nombre no puede estar vacío.
* La licencia debe contener exactamente 10 dígitos.
* La licencia se almacena como texto para conservar posibles ceros iniciales.
* La licencia debe ser única.

## Asignación de conductores

MongoDB almacena solamente la referencia:

```json
{
    "driver_id": "ObjectId"
}
```

La respuesta de la API devuelve el conductor completo:

```json
{
    "id": "ID_DEL_VEHICULO",
    "plate": "PDA-1234",
    "brand": "Toyota",
    "model": "Hilux",
    "year": 2024,
    "capacity_kg": 1000,
    "status": "active",
    "driver": {
        "id": "ID_DEL_CONDUCTOR",
        "name": "Cristian Ca",
        "license": "1234567898"
    }
}
```

Cuando no existe un conductor asignado:

```json
{
    "driver": null
}
```

Un conductor solo puede estar asignado a un vehículo. Al cambiar el conductor de un vehículo, el anterior queda libre automáticamente.

## Pruebas

Ejecuta todas las pruebas con:

```bash
poetry run pytest -v
```

Ejecuta solamente las pruebas de conductores:

```bash
poetry run pytest tests/test_driver_service.py -v
```

Ejecuta las pruebas de asignación:

```bash
poetry run pytest tests/test_vehicle_service.py -v -k "assign_driver"
```

Las pruebas utilizan `AsyncMock` y `MagicMock`, por lo que no necesitan conectarse a una base de datos real.

## Decisiones de implementación

### Referencias en lugar de documentos embebidos

Los vehículos almacenan solamente `driver_id`. No se guarda una copia completa del conductor dentro del vehículo.

Esto evita duplicar información y permite actualizar los datos del conductor desde un único documento.

### Respuestas enriquecidas

Aunque MongoDB almacena `driver_id`, la API devuelve el objeto completo del conductor para que el frontend no tenga que hacer una consulta adicional.

### Índices únicos

Las placas y licencias se protegen mediante índices únicos de MongoDB.

Esto evita duplicados incluso cuando se realizan peticiones simultáneas.

### Validaciones en schemas

Las validaciones de formato se realizan con Pydantic. Las reglas relacionadas con la base de datos y la asignación se manejan dentro de los servicios.

### Seguridad centralizada

La validación del token se realiza mediante la dependencia `get_current_user`, utilizada por todos los endpoints protegidos.

## Mejoras futuras

* Implementar la eliminación de conductores validando que no estén asignados a un vehículo.
* Agregar una operación explícita para dejar un vehículo sin conductor.
* Optimizar el enriquecimiento de vehículos para consultar varios conductores en una sola operación.
* Agregar paginación a las listas de vehículos y conductores.
* Agregar filtros por placa, estado, nombre y licencia.
* Implementar roles y permisos.
* Agregar pruebas de integración para los endpoints.
* Crear un sistema de migraciones o inicialización de índices más estructurado.
