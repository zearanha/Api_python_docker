# Api_python_docker

API REST em Python utilizando Flask, com banco de dados PostgreSQL, tudo rodando via Docker / Docker Compose.

---

## 🧱 Estrutura do Projeto

<b>├── controllers/ # Controladores / rotas da API</b>
├── models/ # Modelos (ORM / classes de dados)
├── services/ # Lógica de “serviços” / regras de negócio
├── Dockerfile # Imagem da aplicação Flask
├── docker-compose.yml # Definições dos serviços (app + postgres)
├── init.sql # Script inicial para o banco (criação de schema, dados iniciais)
├── requirements.txt # Dependências Python
└── app.py # Arquivo principal para rodar a aplicação



---

## ⚙️ Tecnologias

- Python (Flask)  
- PostgreSQL  
- Docker  
- Docker Compose  

---

## 🚀 Como rodar localmente

1. Clone o repositório  
   ```bash
   git clone https://github.com/zearanha/Api_python_docker.git
   cd Api_python_docker


2. Suba os containers
   docker-compose up --build

3. A API estará acessível em http://localhost:5000 (por padrão)
   🛠️ Endpoints (exemplos)

GET /health — Verifica a saúde da aplicação e a conexão com o banco de dados.

POST /login — Autentica um usuário e retorna um token JWT.

POST /users — Cria um novo usuário.

GET /users — Retorna todos os usuários.

GET /users/<id> — Retorna um usuário específico por ID.

PUT /users/<id> — Atualiza um usuário existente

DELETE /recurso/<id> — Deleta um usuário por ID.



📂 Variáveis de ambiente / configuração

No docker-compose.yml (ou possivelmente em um .env) você pode configurar:

POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=nome_do_banco
FLASK_ENV=development


Ajuste conforme necessário.

📦 Scripts de Inicialização

O arquivo init.sql pode conter comandos de criação de tabelas ou inserção de dados iniciais no PostgreSQL.
Se o banco for vazio, ele será inicializado com esse script ao subir o contêiner do Postgres.

🧑‍💻 Autor

zearanha
