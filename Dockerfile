FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium
RUN playwright install-deps

COPY . .

EXPOSE 5000 5001
CMD ["python", "-c", "import subprocess; import threading; def run1(): subprocess.run([\"python\", \"server.py\"]); def run2(): subprocess.run([\"python\", \"app_evaluador.py\"]); t1=threading.Thread(target=run1); t2=threading.Thread(target=run2); t1.start(); t2.start(); t1.join(); t2.join()"]
