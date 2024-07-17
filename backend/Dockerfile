FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install postgres
RUN pip install alembic

RUN apt-get update && apt-get install -y cmake
RUN git clone https://github.com/rism-digital/verovio.git
RUN cd verovio/tools && cmake ../cmake
RUN cd verovio/tools && make
RUN cd verovio/tools && make install

COPY ./app /app/app
COPY ./db /app/db
COPY prod.env .env

COPY main.py main.py
COPY __init__.py __init__.py
COPY alembic.ini alembic.ini
COPY entrypoint.sh entrypoint.sh

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

ENV PORT=8000
EXPOSE 8000
