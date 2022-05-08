TAG_VERSION ?= 1

build-jupyter-notebook:
	docker build -t andreformento/jupyter-notebook:${TAG_VERSION} .

publish-jupyter-notebook: build-jupyter-notebook
	docker push andreformento/jupyter-notebook:${TAG_VERSION}

only-run-jupyter-notebook:
	docker rm -f jupyter-notebook || true
	docker run --network="host" \
			   --name jupyter-notebook \
			   -v "${PWD}/src":/home/jovyan/work/src \
			   -e JUPYTER_ENABLE_LAB=yes \
			   andreformento/jupyter-notebook:${TAG_VERSION}

run-jupyter-notebook: build-jupyter-notebook only-run-jupyter-notebook

run-mlflow:
	docker rm -f mlflow || true
	docker build -t andreformento/mlflow mlflow
	docker run --network="host" \
			   --name mlflow \
			   andreformento/mlflow
