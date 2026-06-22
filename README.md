# agendalink

Sistema de agendamentos com suporte a espaços compartilhados (coworkings, clínicas, estúdios).

## Conceito de Espaço Compartilhado

- **Admin do espaço** cria o espaço e adiciona membros (profissionais)
- **Membros** cadastram seus próprios serviços vinculados ao espaço
- **Agenda coletiva** é opcional — o admin ativa/desativa. Quando ativa, todos os membros veem os agendamentos de todo o espaço
- **Clientes finais** acessam a página pública do espaço, escolhem o profissional e agendam via fluxo conversacional estilo WhatsApp

## Rodar localmente com Docker

### Pré-requisitos
- Docker e Docker Compose instalados

### Subir o projeto

```bash
# Na raiz do projeto
docker compose up --build
```

Acesse: http://localhost:8000

### Criar superusuário (admin)

```bash
docker compose exec web python manage.py createsuperuser
```

### Parar

```bash
docker compose down
```

## Estrutura de URLs

| URL | Descrição |
|-----|-----------|
| `/` | Landing page |
| `/auth/cadastro/` | Criar conta |
| `/auth/login/` | Entrar |
| `/dashboard/` | Painel do usuário |
| `/produtos/novo/` | Cadastrar serviço |
| `/produtos/<id>/disponibilidade/` | Configurar horários |
| `/espaco/meu/novo/` | Criar espaço |
| `/espaco/meu/<slug>/membros/` | Gerenciar membros e agenda coletiva |
| `/espaco/<slug>/` | Página pública do espaço |
| `/espaco/<slug>/profissional/<id>/` | Página pública do profissional |
| `/espaco/<slug>/agendar/<produto_id>/` | Fluxo de agendamento (chat) |
| `/admin/` | Django Admin |

## Variáveis de ambiente (produção/Vercel)

```env
DATABASE_URL=postgres://user:pass@host:5432/dbname   # Supabase connection string
SECRET_KEY=sua-chave-secreta-longa
DEBUG=False
ALLOWED_HOSTS=seu-dominio.vercel.app
```

## Deploy na Vercel

1. Crie um arquivo `vercel.json` na raiz do `app/`:

```json
{
  "builds": [{ "src": "core/wsgi.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "core/wsgi.py" }]
}
```

2. Configure as variáveis de ambiente no painel da Vercel
3. Use o Supabase como banco (copie a connection string do painel do Supabase)

## Stack

- **Aplicação**: Django 5 (monólito)
- **Banco local**: PostgreSQL 16 (Docker)
- **Banco produção**: Supabase (Postgres)
- **Deploy**: Vercel
- **Assets estáticos**: WhiteNoise
- **CSS**: Variáveis CSS nativas, sem framework

## Desenvolvimento com Cursor

- **[AGENTS.md](./AGENTS.md)** — mapa do monólito, domínio, convenções e armadilhas conhecidas para agentes.
- **[.cursor/PROMPTS.md](./.cursor/PROMPTS.md)** — modelos de prompt para features, API, templates, Docker e testes.
- **Regras do projeto:** `.cursor/rules/*.mdc` (aplicadas automaticamente ou por tipo de arquivo).
