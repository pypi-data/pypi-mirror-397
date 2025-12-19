# To build this docker run:
# `docker build -t pylicup`

# To run pylicup in the container:
# `docker run
#   -v /path/to/your/license/file:/mnt/license
#   -v /path/to/your/directory/to/update:/mnt/update
#   pylicup`

FROM python:3.13-slim

# Copy the directories with the local pylicup.
COPY README.md pyproject.toml /app/
COPY pylicup /app/pylicup

# Install pylicup and its dependencies.
RUN pip install --upgrade pip && pip install /app

WORKDIR /app

# Set the entrypoint to run pylicup as a module.
ENTRYPOINT [ "python", "-m", "pylicup", "-l", "/mnt/license", "-d", "/mnt/update" ]