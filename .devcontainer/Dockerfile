FROM python:3.12-slim
#FROM public.ecr.aws/sam/build-python3.12
#FROM public.ecr.aws/docker/library/ubuntu:22.04

USER root

# Add basic tooling
RUN apt update; \
    apt-get install -y \
        ranger \
        btop \
        awscli \
        make \
        pipx \
        npm
        #python3.12 \
RUN pip install git-remote-codecommit

# Setup our non-root user
ARG USERNAME=developer

RUN adduser $USERNAME --shell /bin/zsh

# Setup permissions to persist vscode-server in an anonymous volume
ARG VSC_SERVER_PATH="/home/${USERNAME}/.vscode-server"
VOLUME [ "${VSC_SERVER_PATH}" ]

RUN set -eux; \
    mkdir -p "${VSC_SERVER_PATH}" && \
    chown -R ${USERNAME}:${USERNAME} "/home/${USERNAME}/" && \
    # Work around for Debian not actually doing this itself...
    ln -s /usr/bin/python3.12 /usr/bin/python
    

# Setup user configurations
USER $USERNAME

RUN pipx install poetry==1.8.3 --force && \
    pipx install git-remote-codecommit --force && \
    pipx install pytest --force && \
    pipx ensurepath

ENV POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

    
USER root

CMD [ "sleep", "infinity" ]
