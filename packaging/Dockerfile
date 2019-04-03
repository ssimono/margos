FROM python:3.7

RUN apt update && apt-get install --yes gir1.2-gtk-3.0 libgirepository1.0-dev libgtk-3-0
RUN pip install pyinstaller
COPY ["build/requirements.txt", "/"]
RUN pip install -r /requirements.txt

COPY ["margos", "/workspace"]

WORKDIR "/workspace"
VOLUME "/output"

CMD pyinstaller --specpath /output --distpath /output/dist --workpath /output/work main.py
