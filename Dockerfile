FROM python:3.8
WORKDIR /app
COPY requirements.txt ./requirements.txt # 설치 필요한 라이브러리
RUN pip3 install -r requirements.txt
EXPOSE 8080
COPY . /app
