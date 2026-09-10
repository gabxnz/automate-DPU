# 🚀 Integração Moodle → Power Automate (DPU)

Bem-vindo ao repositório do serviço de automação de inscrições do Moodle da Defensoria Pública da União. Este projeto atua como um **middleware** (serviço intermediário) que escuta eventos do Moodle, enriquece e formata os dados dos alunos e os envia para os fluxos de trabalho no Power Automate.

---

## 📌 1. Visão Geral da Arquitetura

O fluxo completo de automação funciona da seguinte maneira:

```
[Moodle DPU] ──(Webhook HTTP POST)──> [Servidor Flask no Fly.io]
                                                │
                                       (Consulta API Moodle)
                                                │
                                       (Formatação de Dados)
                                                │
                                                ▼
                                    [Power Automate / SharePoint]
```

1. **Evento no Moodle:** Um aluno se inscreve ou atualiza sua inscrição em um curso.
2. **Webhook:** O Moodle dispara uma requisição `POST` para o nosso servidor na nuvem.
3. **Enriquecimento:** O servidor Flask recebe o evento e faz requisições complementares para a API do Moodle (`core_user_get_users_by_field` e `core_course_get_courses`) para obter os campos do perfil do usuário.
4. **Tratamento:** Limpa e padroniza as informações (CPF/Username, Nome Completo, Vínculo, UF, Gênero, Etnia, Município, Nome do Curso).
5. **Entrega:** Envia o JSON limpo para o webhook de gatilho do Power Automate.

---

## 🛠️ 2. Tecnologias e Dependências

- **Linguagem:** Python 3.10+
- **Framework Web:** Flask
- **Servidor WSGI:** Gunicorn
- **Hospedagem:** Fly.io (PaaS 24/7 na região `gru` - São Paulo)
- **Controle de Versão:** Git & GitHub

---

## 📁 3. Estrutura do Projeto

```text
dpu-moodle-automation/
├── app.py              # Código principal (Rotas Flask, chamadas de API e formatação)
├── fly.toml            # Configuração de deploy e infraestrutura no Fly.io
├── requirements.txt    # Dependências do Python (Flask, requests, gunicorn, etc.)
├── .gitignore          # Arquivos e pastas ignorados pelo Git
└── README.md           # Documentação do projeto
```

---

## 💻 4. Configuração do Ambiente de Desenvolvimento

Para rodar ou dar manutenção no projeto na sua máquina local:

### Passo 1: Clonar o repositório
```bash
git clone [https://github.com/SEU-USUARIO/dpu-moodle-automation.git](https://github.com/SEU-USUARIO/dpu-moodle-automation.git)
cd dpu-moodle-automation
```

### Passo 2: Criar e ativar o ambiente virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Passo 3: Instalar as dependências
```bash
pip install -r requirements.txt
```

### Passo 4: Executar a aplicação localmente
```bash
python app.py
```
O servidor estará acessível em `http://localhost:8080`.

---

## ☁️ 5. Gerenciamento e Operação no Fly.io

O serviço roda em nuvem através da CLI do Fly.io (`flyctl`).

* **Autenticar no Fly.io:**
  ```cmd
  flyctl auth login
  ```
* **Acompanhar logs ao vivo (Streaming):**
  ```cmd
  flyctl logs
  ```
* **Verificar status da máquina/servidor:**
  ```cmd
  flyctl status
  ```
* **Publicar atualizações (Deploy):**
  ```cmd
  flyctl deploy
  ```

---

## ⚙️ 6. Configurações Críticas da Nuvem (`fly.toml`)

Para garantir que o servidor **nunca entre em modo de espera (Auto-sleep)** e responda instantaneamente aos webhooks, o arquivo `fly.toml` deve sempre manter as seguintes diretivas no bloco `[http_service]`:

```toml
[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1
```

---

## 🔄 7. Fluxo do Git para Equipes / Estagiários

Antes de alterar qualquer funcionalidade em produção:

1. Baixe as alterações mais recentes da branch principal:
   ```cmd
   git pull origin main
   ```
2. Faça as alterações no código local e teste executando o `app.py`.
3. Suba as alterações para o repositório:
   ```cmd
   git add .
   git commit -m "feat/fix: descrição sucinta da alteração"
   git push origin main
   ```
4. Aplique a nova versão na nuvem do Fly.io:
   ```cmd
   flyctl deploy
   ```

---

## 🚨 8. Resolução de Problemas Comuns (Troubleshooting)

* **O Power Automate parou de receber dados:** 
  Rode `flyctl logs` e verifique se as requisições estão chegando. Se aparecer retornos HTTP `4xx` ou `5xx`, valide o Token de API do Moodle e a URL do Webhook do Power Automate dentro do `app.py`.
* **A aplicação desligou após inatividade:** 
  Confirme se `auto_stop_machines = false` e `min_machines_running = 1` estão ativos no `fly.toml` e execute `flyctl deploy`.
* **Logs travados no terminal:** 
  Aperte `Ctrl + C` para sair da leitura ao vivo dos logs no terminal (isso não encerra o servidor na nuvem).
