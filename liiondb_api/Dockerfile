FROM python:3.11.4

WORKDIR /app

RUN git clone https://github.com/ndrewwang/liiondb.git

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
