#  Select the base Image for running the container with Python
FROM python:3.12

LABEL maintainer="abdulhaseeb065@gmail.com"

# Set the working directory
WORKDIR /code

# Install system dependencies required for potential Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    protobuf-compiler \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy the Pyproject.toml file into the container at /code
COPY ./pyproject.toml /code/

# Configuration to avoid creating virtual environments inside the Docker container
RUN poetry config virtualenvs.create false

# Install all dependencies and packages in Container
RUN poetry install

COPY . /code/

EXPOSE 8085

CMD [ "poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8085", "--reload" ]