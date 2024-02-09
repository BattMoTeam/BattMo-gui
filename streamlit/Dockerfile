FROM python:3.11.4

WORKDIR /app

RUN pip install jill --no-cache-dir

RUN jill install 1.9.2 --confirm

RUN julia -e 'using Pkg; Pkg.add(PackageSpec(;name = "PythonCall",version = "0.9.14"))'

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .