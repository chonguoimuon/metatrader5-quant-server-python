# Stage 1: Base image with apt packages
FROM ghcr.io/linuxserver/baseimage-kasmvnc:debianbullseye-8446af38-ls104 AS base

ENV TITLE=MetaTrader
ENV WINEARCH=win64
ENV WINEPREFIX="/config/.wine"
ENV DISPLAY=:0
ENV DEBIAN_FRONTEND=noninteractive

# Ensure the directory exists with correct permissions
#RUN mkdir -p /config/.wine && \
#    chown -R abc:abc /config/.wine && \
#    chmod -R 755 /config/.wine

# Update package lists and upgrade packages
RUN apt-get update && apt-get upgrade -y

# Install required packages
RUN apt-get install -y \
    dos2unix \
    python3-pip \
    wget \
    python3-pyxdg \
    netcat \
    && pip3 install --upgrade pip

# Add WineHQ repository key and APT source
#RUN wget -q https://dl.winehq.org/wine-builds/winehq.key > /dev/null 2>&1\
#    && sudo apt-key add winehq.key \
#	&& sudo touch /etc/apt/sources.list.d/wine.list \
#    && sudo add-apt-repository 'deb https://dl.winehq.org/wine-builds/debian/ bullseye main' \
#	&& sudo apt-get update \
#    && rm winehq.key 

# Download and store the WineHQ key securely
RUN wget -qO- https://dl.winehq.org/wine-builds/winehq.key \
    | gpg --dearmor \
    | sudo tee /usr/share/keyrings/winehq-archive-keyring.gpg

# Add the WineHQ repository with a reference to the key
RUN echo "deb [signed-by=/usr/share/keyrings/winehq-archive-keyring.gpg] https://dl.winehq.org/wine-builds/debian/ bullseye main" \
    | sudo tee /etc/apt/sources.list.d/winehq.list


# Add i386 architecture and update package lists
RUN sudo dpkg --add-architecture i386 

# Update package lists
RUN apt-get update

# Install WineHQ stable package and dependencies
RUN apt-get install --install-recommends -y \
    winehq-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Final image
FROM base

# Copy the scripts directory and convert start.sh to Unix format
COPY app /app
COPY scripts /scripts
RUN dos2unix /scripts/*.sh && \
    chmod +x /scripts/*.sh

COPY /root /
RUN touch /var/log/mt5_setup.log && \
    chown abc:abc /var/log/mt5_setup.log && \
    chmod 644 /var/log/mt5_setup.log

EXPOSE 3000 5000 5001 8001 18812
VOLUME /config
