FROM python:3.9-slim
ARG USERNAME=API
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --create-home --shell /bin/bash --uid $USER_UID --gid $USER_GID $USERNAME
RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo git ssh
RUN echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}
USER $USERNAME
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"
COPY --chown=$USERNAME:$USERNAME . /app
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e /app