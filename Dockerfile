# Usa uma imagem base oficial do Python
FROM python:3.9-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copia e instala as dependências
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copia o restante do código da sua aplicação
COPY . .

# Expõe a porta que a API usará
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "app.py"]