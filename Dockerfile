FROM python:3.10
COPY main.py ./main.py
COPY requirements.txt ./requirements.txt
WORKDIR .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python3 -m venv .venv
ENTRYPOINT python3 main.py
EXPOSE 5000
