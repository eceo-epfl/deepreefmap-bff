# sensormap-bff
The backend-for-frontend for sensormap


## Getting started

The app requires the following environment variables:
```
KEYCLOAK_CLIENT_ID
KEYCLOAK_REALM
KEYCLOAK_URL
```

To start the app run:

```
KEYCLOAK_CLIENT_ID=test \
    KEYCLOAK_REALM=realmtest \
    KEYCLOAK_URL=https://test.com \
    poetry run uvicorn app.main:app --reload
```

There will be a route available at"

```
http://127.0.0.1:8000/config/keycloak
```