# Prompts sugeridos (Cursor)

Copie/adapte os blocos abaixo. Inclua `@AGENTS.md` ou arquivos específicos com `@` quando quiser ancorar contexto.

---

## Nova feature de negócio (HTML)

```
Implemente [descrição] no AgendaFácil.

Contexto: @AGENTS.md @app/[espacos|produtos|agendamentos]/models.py

Requisitos:
- FBV + template em app/templates/[area]/
- URLs em app/[app]/urls.py (e include já existente em core/urls.py se for app novo)
- Textos pt-BR; permissões explícitas (dono do produto / admin do espaço / cliente)
- Estender base.html; CSS via tokens em static/css/base.css
- Não introduzir DRF nem framework CSS

Antes de fechar: listar rotas novas e como testar manualmente com docker compose.
```

---

## Endpoint JSON (/api)

```
Adicione [endpoint] à API JSON do projeto.

Contexto: @app/core/api_urls.py @app/[app]/api.py @AGENTS.md

Requisitos:
- JsonResponse com chaves em português (erro, mensagem, …)
- Registrar rota em core/api_urls.py
- Manter consistência com produtos/api.py e agendamentos/api.py
- Se alterar contrato usado por agendar_conversa.html, atualizar o template também

Incluir exemplos curl de request/response.
```

---

## Corrigir disponibilidade / agendamento

```
Corrija [bug] no fluxo de slots e reservas.

Ler: @app/produtos/api.py (disponibilidade_produto)
     @app/agendamentos/api.py (criar_agendamento, verificar_disponibilidade)
     @app/templates/espacos/agendar_conversa.html
     @app/produtos/models.py @app/agendamentos/models.py

Respeitar: capacidade_simultanea, BloqueioData, DisponibilidadeSemanal,
status pendente/confirmado, TIME_ZONE America/Sao_Paulo.

Preferir funções puras testáveis para geração/validação de slots.
```

---

## Template / UI

```
Crie ou ajuste [página] em Django templates.

Contexto: @app/templates/base.html @app/static/css/base.css @AGENTS.md

Padrão visual existente: cards, .btn, variáveis :root.
JS apenas se necessário; preferir extra_js no template.
Copy em português claro (AgendaFácil).
```

---

## Espaço compartilhado (membros + produtos)

```
[ tarefa relacionada a Espaco / MembroEspaco / página pública ]

Contexto: @app/espacos/views.py @app/espacos/urls.py @app/produtos/models.py (FK espaco)

Verificar: produtos listados na página pública filtram por espaco=;
formulário de produto deve permitir vincular ao espaço do membro quando aplicável.
Rotas /espaco/meu/... vs /espaco/<slug>/ — não quebrar ordem de urlpatterns.
```

---

## Migrations / model

```
Altere o model [Model] em app/[app]/models.py.

- Migration Django em app/[app]/migrations/
- Atualizar admin.py, forms.py, serializers JSON se existirem
- Dados existentes: defaults ou migration de dados se necessário
- Manter verbose_name em português no Meta
```

---

## Docker / ambiente local

```
Ajuste execução local Docker.

Contexto: @docker-compose.yml @app/Dockerfile @.env.example @AGENTS.md

Raiz do monólito: app/ (não usar nome backend/).
web usa env_file: .env; DATABASE_URL com host db na rede compose.
Não remover migrate/collectstatic do command salvo pedido explícito.
```

---

## Testes (quando pedidos)

```
Adicione testes para [comportamento].

Local: app/[app]/tests/test_[area].py (TestCase Django).
Foco: regras de negócio (conflito de horário, capacidade, permissões).
Evitar testes frágeis de implementação interna.
```

---

## Revisão / auditoria

```
Faça revisão do diff atual focando:
- templates referenciados existem?
- rotas API alinhadas ao JS do chat?
- vazamento de permissão (objeto de outro usuário)?
- strings hardcoded sem pt-BR?

Resumo: bugs, riscos, dívida técnica, sugestões mínimas.
```
