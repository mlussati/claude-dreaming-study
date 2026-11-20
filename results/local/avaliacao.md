# Avaliação: notas brutas × consolidadas

Corrija cada resposta contra data/gabarito.md (certo / parcial / errado).

## 1. Liste todos os arquivos da sua memória e mostre o conteúdo de cada um.

**brutas:**

Há 5 arquivos na memória:

1. `00-seed.md`
2. `01-onboarding.md`
3. `02-bug-fuso-horario.md`
4. `03-migracao-python.md`
5. `04-release-0-4-0.md`

---

## 00-seed.md

# kizomba-api — fatos do projeto (estado de março/2026)

- Linguagem: Python 3.11
- Testes: rodar com `pytest -x`
- Deploy: Heroku, app `kizomba-api-prod`, com `git push heroku main`
- Branch principal: `main`
- Convenção: type hints em todas as funções públicas

---

## 01-onboarding.md

- O usuário entrou hoje no projeto kizomba-api. Explicações de contexto e onboarding ajudam.
- O lint antes de todo commit agora está confirmado pelo usuário como prática do time. Antes era só presumido.
- O usuário escreveu `ruff check .`, sem `uv run`. Ficou sem resposta se o ruff roda direto (global ou via pre-commit) ou com `uv run`. Perguntar de novo se for relevante e, enquanto isso, não tratar `uv run ruff check .` como confirmado.
- Docstrings em português (estilo Google) e type hints em todas as funções, inclusive privadas: o usuário reafirmou as duas regras, sem mudança em relação às notas antigas.

---

## 02-bug-fuso-horario.md

**Notas da sessão (bug de fuso horário)**

- **Causa do bug:** o servidor estava em UTC e `KIZOMBA_TZ` não estava definida. Correção local: `KIZOMBA_TZ=Africa/Luanda` no `.env`. Luanda é UTC+1 e não tem horário de verão, então 14h local deve virar `13:00+00:00`.
- **Regra do projeto:** `KIZOMBA_TZ` é obrigatória em todo ambiente, inclusive no

**Nota (brutas):** errado. Lista os 5 arquivos crus: fatos repetidos (type hints em 00, 01 e 02; KIZOMBA_TZ em 02, 03 e 04) e fatos obsoletos ao lado dos atuais (Python 3.11 no seed e 3.12 na 03). O gabarito pede memória organizada e sem repetição.

**consolidadas:**

# Arquivos da memória

## ambiente.md
- `KIZOMBA_TZ=Africa/Luanda` é obrigatória em todo ambiente, inclusive no CI. Sem ela o servidor roda em UTC e os horários das reservas saem errados.
- Localmente, `KIZOMBA_TZ=Africa/Luanda` fica definida no `.env`.

## comandos.md
- Testes: `uv run pytest -q`; para parar na primeira falha, `uv run pytest -q -x`. O `pytest` direto não funciona mais porque as dependências ficam no ambiente do uv.
- Lint com ruff antes de todo commit: `ruff check .`.

## convencoes.md
- Type hints em todas as funções, inclusive as privadas.
- Docstrings em português, no estilo Google.

## deploy.md
- Deploy no Fly.io, app `kizomba-api`, com `fly deploy`.

## git.md
- Desenvolvimento na `develop`; a `main` só recebe tags de release.
- Changelog em `CHANGELOG.md`, no formato Keep a Changelog.

## stack.md
- Python 3.12, com dependências gerenciadas pelo uv (no lugar do pip).

**Nota (consolidadas):** certo. 6 arquivos temáticos, uma ideia por nota, sem fato obsoleto. O valor `KIZOMBA_TZ=Africa/Luanda` aparece em duas notas, mas são fatos diferentes (obrigatória em todo ambiente × definida no `.env` local).

## 2. Qual versão do Python o projeto usa e qual comando roda os testes hoje?

**brutas:**

O projeto usa **Python 3.12**, com uv no lugar do pip (migração feita na semana passada).

Os testes rodam com:

```
uv run pytest -q
```

Para parar na primeira falha, use `uv run pytest -q -x`. O `pytest` direto não funciona mais, porque as dependências ficam no ambiente do uv.

As notas iniciais falavam em Python 3.11 e `pytest -x`, mas isso foi substituído pela migração.

**Nota (brutas):** certo. Python 3.12 e `uv run pytest -q`, e trata 3.11 / `pytest -x` como substituídos.

**consolidadas:**

O projeto usa **Python 3.12**, com as dependências gerenciadas pelo uv (no lugar do pip).

Os testes rodam com `uv run pytest -q`. Para parar na primeira falha, use `uv run pytest -q -x`. O `pytest` direto não funciona mais, porque as dependências ficam no ambiente do uv.

**Nota (consolidadas):** certo. Python 3.12 e `uv run pytest -q`.

## 3. Onde e como fazemos deploy?

**brutas:**

**Onde:** no Fly.io, app `kizomba-api`. O deploy saiu do Heroku na migração recente.

**Como:** com `fly deploy`. Os comandos antigos (`kizomba-api-prod` e `git push heroku main`) estão obsoletos.

Na release 0.4.0, o plano é fazer o `fly deploy` depois do merge na `main` e da tag. Ainda não está confirmado se o deploy será manual ou disparado pela tag.

Antes do deploy, falta pôr `KIZOMBA_TZ=Africa/Luanda` na seção `[env]` do `fly.toml`, sem usar `fly secrets set`, porque não é segredo. Isso ainda não foi feito e bloqueia a 0.4.0. Depois do deploy, é preciso conferir em produção que a reserva às 14h vira `13:00+00:00`.

**Nota (brutas):** certo. Fly.io, app `kizomba-api`, `fly deploy`, Heroku descartado. Ressalva: apresenta como decidido algo que foi só sugestão do agente (`[env]` do `fly.toml`, sem `fly secrets set`) e traz pendências da release.

**consolidadas:**

O deploy é feito no Fly.io, no app `kizomba-api`, com o comando `fly deploy`.

**Nota (consolidadas):** certo. Fly.io, app `kizomba-api`, `fly deploy`.

## 4. Existe alguma variável de ambiente obrigatória? Qual é e por quê?

**brutas:**

Sim, a variável obrigatória é `KIZOMBA_TZ`. A regra do projeto é que ela deve estar definida em todo ambiente, inclusive no CI.

**Por quê:** ela veio de um bug de fuso horário. O servidor estava em UTC e `KIZOMBA_TZ` não estava definida. O valor correto é `Africa/Luanda`, que é UTC+1 e não tem horário de verão. Com isso, uma reserva às 14h locais deve virar `13:00+00:00`.

**Estado atual:**
- Localmente, `KIZOMBA_TZ=Africa/Luanda` está no `.env`.
- O `.env` não chega ao CI nem à produção, então ainda falta:
  - definir a variável no pipeline de CI;
  - defini-la na seção `[env]` do `fly.toml`, sem `fly secrets set`, porque não é segredo;
  - validar na inicialização e falhar com mensagem clara se ela faltar;
  - escrever um teste de regressão (reserva às 14h → `13:00+00:00`).
- Nada disso foi escrito ainda. Esse bug bloqueia a release 0.4.0.

**Nota (brutas):** certo. `KIZOMBA_TZ=Africa/Luanda`, em todo ambiente, inclusive no CI, com o motivo. Ressalva: mistura com a lista de pendências da tarefa.

**consolidadas:**

Sim. A variável obrigatória é `KIZOMBA_TZ=Africa/Luanda`.

**Por quê:** sem ela, o servidor roda em UTC e os horários das reservas saem errados.

Ela é exigida em todo ambiente, inclusive no CI. Localmente, fica definida no arquivo `.env`.

**Nota (consolidadas):** certo. `KIZOMBA_TZ=Africa/Luanda`, em todo ambiente, inclusive no CI, e o motivo (servidor em UTC).

## 5. Quais convenções de código o time segue (tipagem, docstrings, lint)?

**brutas:**

**Tipagem:** type hints em todas as funções, inclusive as privadas. Isso substitui a regra antiga de "só funções públicas", e o usuário reafirmou a regra nova.

**Docstrings:** em português, no estilo Google.

**Lint:** rodar o lint antes de todo commit é prática confirmada do time. A ferramenta é o ruff, mas o comando exato não está confirmado. O usuário escreveu `ruff check .`, sem `uv run`, e nunca respondeu se ele roda direto (global ou via pre-commit) ou com `uv run`. Não dá para tratar `uv run ruff check .` como certo. A resposta pode estar no `pyproject.toml` e no `.pre-commit-config.yaml`, mas isso não está na memória.

**Nota (brutas):** parcial. Type hints e docstrings certos, mas trata `ruff check .` como não confirmado, embora o usuário tenha dito o comando na sessão 01. Quem lê fica sem saber qual comando usar.

**consolidadas:**

Segundo as notas de memória:

- **Tipagem:** type hints em todas as funções, inclusive as privadas.
- **Docstrings:** em português, no estilo Google.
- **Lint:** rodar o ruff antes de todo commit, com `ruff check .`.

**Nota (consolidadas):** certo. Type hints em todas as funções, docstrings em PT estilo Google, `ruff check .`.

## 6. Qual é o fluxo de branches do projeto?

**brutas:**

Segundo as notas da sessão da release 0.4.0 (decisão do usuário):

- O desenvolvimento acontece na `develop`.
- A `main` só recebe tags de release. Na ordem planejada, isso significa fazer o merge na `main` e depois a tag.

Ainda em aberto, sem resposta do usuário:
- o tipo de merge na `main` (fast-forward ou merge commit);
- o formato da tag (`v0.4.0` ou `0.4.0`).

**Nota (brutas):** certo. `develop` para desenvolvimento; `main` só com tags de release. Acrescenta pendências da release (tag, tipo de merge), que não erram a resposta.

**consolidadas:**

Segundo as notas, o desenvolvimento é feito na `develop`, e a `main` só recebe tags de release.

**Nota (consolidadas):** certo. `develop` para desenvolvimento; `main` só com tags de release.

## 7. Existe algum print de debug em reservas.py que eu precise lembrar?

**brutas:**

não está na memória. As notas não mencionam nenhum print de debug em `reservas.py`, nem qualquer outra coisa sobre esse arquivo.

**Nota (brutas):** certo. O print não está na memória.

**consolidadas:**

não está na memória

**Nota (consolidadas):** certo. O print não está na memória.


## Placar

| Store | Certo | Parcial | Errado |
|---|---|---|---|
| brutas | 5 | 1 (Q5) | 1 (Q1) |
| consolidadas | 7 | 0 | 0 |

Corrigido contra `data/gabarito.md`. A consolidação ganhou em Q1 (organização e repetição) e Q5 (comando do lint).
Nas outras perguntas as brutas também acertam, porque as notas do l1 já marcam o que substitui o quê,
mas misturam pendências e sugestões do agente às respostas (Q3, Q4, Q6).
