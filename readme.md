# Projecte de fi de grau
## Control remot de dispositius de communicacions

## Configuració

### .env
Per a configurar el projecte, cal crear un fitxer .env a la carpeta arrel del projecte amb les següents variables d'entorn:
```
MYSQL_PORT=3306

DATABASE_HOST="mysql"
DATABASE_USERNAME="flask_app"
DATABASE_PASSWORD="{PASSWORD DATABASE}"
MYSQL_ROOT_PASSWORD="{PASSWORD DATABASE}"
CRSF_KEY=""{PASSWORD CRSF}"

FLASK_APP_IP=172.22.0.22
MYSQL_IP=172.22.0.11
```

### Docker
Per a executar el projecte, cal tenir instal·lat Docker i Docker Compose. Un cop instal·lat, cal executar la següent comanda a la carpeta arrel del projecte:
```
docker-compose up --build
```

### Inicialització de la base de dades
Per a inicialitzar la base de dades, cal tindre en compte el fitxer init.sql que conté les taules i dades inicials. Aquest fitxer s'executarà automàticament en el moment de crear el contenidor de la base de dades.

