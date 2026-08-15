FROM python:3.13
USER root

RUN apt-get update
RUN pip install --upgrade pip

RUN python -m pip install discord.py
RUN python -m pip install aiohttp
RUN python -m pip install asyncio
RUN python -m pip install Path
RUN python -m pip install json

COPY ./work /work
WORKDIR /work
CMD ["python", "osuServer.py"]