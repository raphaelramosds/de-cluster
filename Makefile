# Define the default target
.PHONY: all
all: download build

# Target to download dependencies
.PHONY: download
download:
	bash download.sh

# Target to build the Docker image
.PHONY: build
build:
	docker compose build airflow-webserver
	docker compose build spark-master

# Clean target (optional, if you want a cleanup step)
.PHONY: clean
clean:
	docker compose down --volumes