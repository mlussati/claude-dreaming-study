# Gabarito / Answer key

O que a memória **depois** do dream deveria responder. A memória **antes** (só o seed) deve errar os itens marcados com ⚠️.
What the memory **after** the dream should answer. The memory **before** (seed only) should get the ⚠️ items wrong.

| # | Pergunta / Question | Esperado / Expected | Tipo de teste / Test type |
|---|---|---|---|
| 1 | Arquivos da memória / memory files | Organizados, sem fatos repetidos / organized, no repeated facts | Consolidação / consolidation |
| 2 | Python e testes / Python and tests | ⚠️ Python 3.12, `uv run pytest -q` (não 3.11 / `pytest -x`) | Contradição / contradiction |
| 3 | Deploy | ⚠️ Fly.io, app `kizomba-api`, `fly deploy` (não Heroku) | Contradição / contradiction |
| 4 | Variável obrigatória / required env var | ⚠️ `KIZOMBA_TZ=Africa/Luanda`, em todo ambiente, inclusive CI | Detalhe enterrado / buried detail |
| 5 | Convenções / conventions | ⚠️ type hints em **todas** as funções; docstrings em PT, estilo Google; `ruff check .` | Atualização + duplicata / update + duplicate |
| 6 | Branches | ⚠️ desenvolvimento na `develop`; `main` só recebe tags de release | Contradição / contradiction |
| 7 | Print de debug / debug print | Não deve estar na memória (foi resolvido) / should not be in memory (resolved) | Ruído / noise |

Fato novo esperado / new fact expected: changelog em `CHANGELOG.md`, formato Keep a Changelog.
