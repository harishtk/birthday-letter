FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home birthday
USER birthday
ENV PORT=5000
EXPOSE 5000
CMD ["python", "serve.py"]
