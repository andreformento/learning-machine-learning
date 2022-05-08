TAG_VERSION ?= 0.0.1

build:
	docker build -t andreformento/jupyter-notebook:${TAG_VERSION} .

publish: build
	docker push andreformento/jupyter-notebook:${TAG_VERSION}

start:
	docker rm -f jupyter-notebook || true
	docker run --network="host" \
			   --name jupyter-notebook \
			   -v "${PWD}/src":/home/jovyan/work/src \
			   -e JUPYTER_ENABLE_LAB=yes \
			   andreformento/jupyter-notebook:${TAG_VERSION}

run-mlflow:
	docker rm -f mlflow || true
	docker build -t andreformento/mlflow mlflow
	docker run --network="host" \
			   --name mlflow \
			   andreformento/mlflow
