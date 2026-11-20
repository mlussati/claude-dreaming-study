# Decisões da consolidação (l2)

Modelo: `claude-sonnet-5-5`. Regras: ver `INSTRUCTIONS` em `local/l2_consolidar.py`.

## Notas finais

| Arquivo | Nota | Operação | Origens | Vencidas | Regra | Evidência (fala do usuário) |
|---|---|---|---|---|---|---|
| stack.md | Python 3.12, com dependências gerenciadas pelo uv (no lugar do pip). | substituida | 03#1 | 00#1 | R2 | s03: semana passada migramos o kizomba-api para Python 3.12 e trocamos o pip pelo uv. |
| comandos.md | Testes: `uv run pytest -q`; para parar na primeira falha, `uv run pytest -q -x`. O `pytest` direto não funciona mais porque as dependências ficam no ambiente do uv. | substituida | 03#2 | 00#2 | R2 | s03: O `pytest -x` direto não funciona mais, porque as dependências ficam no ambiente do uv. |
| comandos.md | Lint com ruff antes de todo commit: `ruff check .`. | fundida | 01#2, 01#3 |  | R3 | s01: o lint é com ruff: rodamos `ruff check .` antes de todo commit |
| deploy.md | Deploy no Fly.io, app `kizomba-api`, com `fly deploy`. | substituida | 03#3 | 00#3 | R2 | s03: o deploy agora é no Fly.io, app `kizomba-api`, com `fly deploy`. |
| git.md | Desenvolvimento na `develop`; a `main` só recebe tags de release. | substituida | 04#1 | 00#4 | R2 | s04: o desenvolvimento agora acontece na `develop`, e a `main` só recebe tags de release. |
| git.md | Changelog em `CHANGELOG.md`, no formato Keep a Changelog. | mantida | 04#2 |  | R4 | s04: O changelog fica em `CHANGELOG.md`, no formato Keep a Changelog. |
| convencoes.md | Type hints em todas as funções, inclusive as privadas. | substituida | 01#4, 02#4 | 00#5 | R2 | s01: agora a gente coloca type hints em todas as funções, inclusive nas privadas, não só nas públicas. |
| convencoes.md | Docstrings em português, no estilo Google. | fundida | 01#4, 02#4 |  | R3 | s01: docstrings em português, no estilo Google |
| ambiente.md | `KIZOMBA_TZ=Africa/Luanda` é obrigatória em todo ambiente, inclusive no CI. Sem ela o servidor roda em UTC e os horários das reservas saem errados. | fundida | 02#1, 02#2 |  | R3 | s02: essa variável é obrigatória em todo ambiente, inclusive no CI. |
| ambiente.md | Localmente, `KIZOMBA_TZ=Africa/Luanda` fica definida no `.env`. | mantida | 02#1 |  | R4 | s02: Resolvi definindo `KIZOMBA_TZ=Africa/Luanda` no `.env` |

## Notas descartadas

| ID | Nota bruta | Regra | Motivo |
|---|---|---|---|
| 01#1 | O usuário entrou hoje no projeto kizomba-api. Explicações de contexto e onboarding ajudam. | R4 | contexto de onboarding/pessoal do usuário, não é fato técnico durável |
| 02#3 | **Pendente (o `.env` não chega ao CI nem à produção):**   - Definir `KIZOMBA_TZ=Africa/Luanda` nas variáveis do pipeline de CI.   - Definir a variável na seção  | R1 | pendências e sugestões do agente (fly.toml [env], validação, teste) que o usuário não confirmou; também são TODOs (R4) |
| 03#4 | **Pendente, fuso horário:** `KIZOMBA_TZ=Africa/Luanda` ainda não está configurada no Fly.io nem no CI.   - Sugestão minha, ainda não confirmada: pôr no `[env]`  | R1 | sugestão do agente não confirmada e pendência de tarefa, não é fato durável |
| 03#5 | **Em aberto:** ainda não sei o comando certo do ruff (`uv run ruff check .`, global ou pre-commit). Perguntei duas vezes e o usuário não respondeu. Perguntar de | R4 | pergunta em aberto do agente; o usuário já informou `ruff check .`, registrado na nota de lint |
| 04#3 | **Bug do fuso horário (bloqueia a 0.4.0):**   - `KIZOMBA_TZ=Africa/Luanda` precisa estar no CI e em `[env]` do `fly.toml`. Não é segredo, então não usa `fly sec | R1 | plano do bug do fuso feito pelo agente; a obrigatoriedade de KIZOMBA_TZ já está na nota de ambiente, o resto é pendência (R4) |
| 04#4 | **Ordem planejada:**   1. Lint e testes na `develop`.   2. Correção do fuso.   3. Changelog.   4. Versão 0.4.0.   5. Merge na `main` e tag.   6. `fly deploy`.   | R4 | plano/checklist da release 0.4.0, não é fato durável |
| 04#5 | **Estado:** só o planejamento foi feito. Nenhum arquivo foi alterado e nenhum comando foi rodado. | R4 | estado momentâneo de uma tarefa, não é fato durável |
| 04#6 | **Pendente, o usuário não respondeu:**   - Comando do lint: `ruff check .` ou `uv run ruff check .` (dá para conferir no `pyproject.toml` e no `.pre-commit-conf | R1 | lista de perguntas sem resposta do usuário (suposições do agente), não são fatos |
| 04#7 | **Próximo passo sugerido:** começar pela validação do `KIZOMBA_TZ` e pelo teste de regressão. | R4 | sugestão de próximo passo, plano de tarefa |

## Verificação automática

- ok: todas as notas brutas tratadas e todas as citações conferem.
