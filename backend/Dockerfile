FROM python:3.11-slim-bookworm


ARG CODE=/code

# Make base folder for the source code
RUN mkdir ${CODE}

# Copy local code to container location and change working dir to that directory
WORKDIR ${CODE}

COPY . ${CODE}

RUN apt-get update && apt-get install -y git

# Install the python packages
RUN pip install -r ${CODE}/requirements.txt

# Expose the port
EXPOSE 8007

# Default command for the image (this can be overwritten on compose)
CMD ["bash", "run_server.sh"]

