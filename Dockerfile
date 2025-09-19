FROM ubuntu:22.04

WORKDIR /app

RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y --no-install-recommends wget gnupg ca-certificates

RUN wget -O /tmp/winehq.key https://dl.winehq.org/wine-builds/winehq.key

RUN gpg --dearmor -o /usr/share/keyrings/winehq-archive-keyring.gpg < /tmp/winehq.key && \
    echo 'deb [signed-by=/usr/share/keyrings/winehq-archive-keyring.gpg] https://dl.winehq.org/wine-builds/ubuntu/ jammy main' > /etc/apt/sources.list.d/winehq.list
    
RUN apt-get update && \
    apt-get install -y --no-install-recommends winehq-stable winetricks cabextract

RUN wget -qO /tmp/py_inst.exe https://www.python.org/ftp/python/3.9.7/python-3.9.7.exe

RUN wineboot --init && \
    winetricks -q corefonts && \
    wine /tmp/py_inst.exe /S /v/qn


RUN rm /tmp/py_installer.exe /tmp/winehq.key