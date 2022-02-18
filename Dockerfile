FROM python:3.9.6

RUN apt-get update \
    && apt-get install --no-install-recommends --yes \
     build-essential \
     python3 \
     python3-pip \
     python3-dev

COPY requirements.txt .
RUN pip3 install --compile --no-cache-dir -r requirements.txt

COPY Assignments/assignment4.py .
COPY Assignments/midterm.py .
COPY Assignments/cat_correlation.py .
COPY Assignments/hw4_data.py .
COPY Assignments/final.py .
COPY Assignments/finalsql.sql .

RUN mkdir finalTables/


CMD ["python", "final.py"]

