FROM python:3.10

RUN apt-get update && apt-get install -y \
    python3-opencv

WORKDIR /src

RUN pip3 install --upgrade pip

COPY requirements.txt /src/requirements.txt
RUN pip3 install -r requirements.txt

COPY . /src
EXPOSE 5000
CMD [ "python", "sgmk2-cv.py" ]