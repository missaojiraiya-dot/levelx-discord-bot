# LevelX Discord Bot

Bot Discord self-bot com sistema de autorização para múltiplos usuários.

## Deploy no Railway

### 1. Preparação
1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha este repositório

### 2. Configuração das Variáveis
No painel do Railway, vá em **Variables** e adicione:
```
DISCORD_TOKEN=seu_token_aqui
```

### 3. Deploy
- O Railway detecta automaticamente que é um projeto Python
- Usa o arquivo `Procfile` para saber como rodar
- Instala dependências do `requirements.txt`
- Bot fica online 24/7!

## Comandos Principais

- `lx!addperm <user_id>` - Adiciona permissão para usuário
- `lx!remoteuser ADD @usuario` - Adiciona usuário autorizado
- `lx!help` - Lista todos os comandos

## Recursos

- ✅ Sistema de autorização para múltiplos usuários
- ✅ Comandos de moderação (`lx!puxar`, `lx!marcar`)
- ✅ Auto-reply e AFK
- ✅ Processamento de comandos para usuários autorizados

## Developed by Tio Sunn'212