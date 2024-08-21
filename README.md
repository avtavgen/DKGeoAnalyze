# fastapi-example

FastAPI Rest example project.

## Preconditions:

- Python 3.12
- PostgreSQL

## Clone the project

```
git clone https://github.com/avtavgen/DKTest.git
```

## Run local

### Setup virtual environment

```
python -m venv venv
source venv/bin/activate
```

### Install dependencies

```
pip install -r requirements.txt
```

### Run server

```
fastapi run main.py
```

### Run tests

```
pytest tests/tests.py
```

## Run with docker

### Run server (http://0.0.0.0/)

```
$ docker-compose up -d --build
$ docker-compose exec web alembic upgrade head
```

### Run tests

```
docker-compose exec web pytest tests/tests.py
```

## API documentation

```
http://0.0.0.0/docs
```