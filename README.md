# 🚀 Automação Moodle → Power Automate (DPU)

Este serviço recebe as inscrições do Moodle da DPU, busca as informações do aluno e envia tudo formatado para o Power Automate registrar na planilha.

---

## 🔄 Como funciona?

`Moodle (Webhook)` ➔ `Flask (Render.com)` ➔ `Power Automate` ➔ `Planilha Excel`

---

## ⚙️ Variáveis no Render.com

No painel do Render.com (aba **Environment Variables**), adicione:

* **`MOODLE_API_URL`**: `https://ead.dpu.def.br` *(apenas a URL limpa)*
* **`MOODLE_API_TOKEN`**: Token do WebService do Moodle
* **`POWER_AUTOMATE_URL`**: URL de gatilho do Power Automate
* **`FLASK_PORT`**: `8080`

---

## 💻 Como atualizar o projeto?

1. Baixe o código mais recente:
   ```bash
   git pull origin main
   ```
2. Faça as alterações necessárias e envie para o GitHub:
   ```bash
   git add .
   git commit -m "ajuste: explicacao simples da mudanca"
   git push origin main
   ```
3. O Render atualiza a aplicação sozinho na nuvem logo após o `git push`.

---

## ⏱️ Servidor sempre ativo (UptimeRobot)

O plano gratuito do Render entra em modo de espera após 15 minutos sem uso.  
Para mantê-lo rodando 24 horas sem custos:
1. Cadastre a URL do seu Render no **[UptimeRobot](https://uptimerobot.com)**.
2. Configure um teste HTTP para disparar a cada **10 minutos**.

---

## 🚨 Resolução de Erros

* **Planilha parou de atualizar:** Acesse o Render.com, clique na sua aplicação e vá na aba **Logs** para ver o erro em tempo real.
* **Erro de URL no Moodle:** Certifique-se de que a variável `MOODLE_API_URL` não tem aspas, colchetes ou espaços.
