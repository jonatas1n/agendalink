# AgendaFácil — guia para agentes (Cursor)

Monólito **Django 5** de agendamentos com **espaços compartilhados** (coworkings, clínicas, estúdios). Código da aplicação em `app/`; orquestração local na raiz com Docker Compose.

## Mapa rápido

| O quê | Onde |
|-------|------|
| Settings, URLs raiz, landing, auth, dashboard | `app/core/` |
| Espaços, membros, páginas públicas, chat de agendamento | `app/espacos/` |
| Serviços/produtos, disponibilidade semanal | `app/produtos/` |
| Reservas (modelo + listagem/cancelamento HTML) | `app/agendamentos/` |
| API JSON (`/api/…`) | `app/produtos/api.py`, `app/agendamentos/api.py`, rotas em `app/core/api_urls.py` |
| Templates | `app/templates/` (por feature: `espacos/`, `produtos/`, …) |
| CSS/JS global | `app/static/css/base.css`, `app/static/js/base.js` |
| Compose / env | `docker-compose.yml`, `.env` (copiar de `.env.example`) |

## Domínio (leia antes de modelar dados)

1. **Espaco** — venue; `admin` é o dono; slug único; `agenda_coletiva_ativa` opcional.
2. **MembroEspaco** — vínculo User ↔ Espaco (`papel`, `status`).
3. **Produto** — serviço agendável; `proprietario`; FK opcional `espaco`; soft delete `ativo`.
4. **DisponibilidadeSemanal** / **BloqueioData** — janelas e bloqueios por produto.
5. **Agendamento** — slot reservado; status `pendente`/`confirmado`/…; cliente = `User`.

Auth: **User padrão do Django** (sem custom user model).

## Convenções

- **Idioma:** textos de UI, labels, mensagens e chaves JSON voltadas ao usuário em **português (pt-BR)**. Estrutura Python/Django em inglês (`related_name`, nomes de funções internas).
- **Views:** apenas **function-based views**; `@login_required` onde couber; permissões no objeto (`proprietario`, admin do espaço, cliente).
- **API:** funções que retornam `JsonResponse` — **não** há DRF. Novas rotas JSON entram em `api.py` do app e em `core/api_urls.py`.
- **Templates:** estender `base.html`; blocos `title`, `content`, `extra_css`, `extra_js`. Sem React/Vite; JS vanilla inline ou em `static/`.
- **Estilo:** variáveis CSS em `base.css`; **não** adicionar Bootstrap/Tailwind salvo pedido explícito.
- **Early exit** em views/API: validar e retornar cedo; evitar `if/else` profundos.

## Comandos úteis

```bash
# Na raiz do repositório
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser

# Fora do Docker (com DATABASE_URL apontando para Postgres local)
cd app && python manage.py runserver
```

## Fluxo crítico: agendamento conversacional

Template `app/templates/espacos/agendar_conversa.html` consome:

- `GET /api/produtos/<id>/disponibilidade/` — slots (~60 dias)
- `POST /api/agendamentos/criar/` — JSON `{ produto_id, data_hora, observacoes }`; **exige login**

Alterações em disponibilidade ou criação de agendamento devem manter esse contrato e respeitar `capacidade_simultanea` e status `pendente`/`confirmado`.

## Armadilhas conhecidas (não ignore)

- **Templates ausentes** referenciados em views: `produtos/lista.html`, `detalhe.html`, `agendar.html`, `confirmar_exclusao.html`, `agendamentos/detalhe.html`. Verificar antes de assumir rotas completas.
- **Produto.espaco:** o model tem FK; formulários atuais podem não preencher — serviços podem não aparecer na página pública do espaço até ligar `espaco` na UI.
- **Guest no chat:** UI coleta dados, mas a API exige `User` autenticado.
- **`csrf_exempt`** em alguns POSTs da API — tratar com cuidado em mudanças de segurança.
- **Timezone:** lógica de slots mistura datetimes naive/aware; testar com `America/Sao_Paulo`.
- **Não commitar** `.env`; credenciais só em `.env.example` como placeholders.

## O que este projeto não é

- Sem frontend separado, sem DRF, sem pasta `components/` de templates.
- `django-environ` está no requirements mas settings usa `os.environ.get`.
- Deploy alvo (README): Vercel + Supabase; `vercel.json` documentado no README, pode não existir no repo.

## Qualidade esperada ao implementar

- Preferir diff mínimo e alinhado ao código existente.
- Novas features de negócio: app Django correto + template + URL + (se AJAX) entrada em `api_urls.py`.
- Lógica não trivial de datas/ocupação: extrair função testável e considerar testes em `app/<app>/tests/`.
- Remover imports mortos ou usar forms/formsets já definidos (ex.: `DisponibilidadeFormSet`).

## Documentação Cursor

- Regras persistentes: `.cursor/rules/*.mdc`
- Prompts prontos para tarefas comuns: `.cursor/PROMPTS.md`
