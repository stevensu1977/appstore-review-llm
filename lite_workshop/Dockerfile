# Start from a core stack version
FROM jupyter/base-notebook:latest


USER root
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y git && apt-get clean && rm -rf /var/lib/apt/lists/*


# Install from requirements.txt file
USER $NB_UID
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/
RUN pip install --quiet --no-cache-dir --requirement /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
#upgrade boto3 to support nativate function calling
RUN pip install --upgrade boto3 && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"



EXPOSE 8888
