FROM python:3.11.4

WORKDIR /app

RUN git clone https://github.com/ndrewwang/liiondb.git


ENV PYTHONPATH="${PYTHONPATH}:/app/liiondb/functions"
# Print Python path
RUN python -c "import sys; print(sys.path)"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .


