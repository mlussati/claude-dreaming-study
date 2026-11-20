<!-- Testa: CONTRADIÇÃO com a memória inicial (Python, comando de teste, deploy). -->
<!-- Tests: CONTRADICTS the initial memory (Python version, test command, deploy). -->
Novidade: semana passada migramos o kizomba-api para Python 3.12 e trocamos o pip pelo uv.
---
Os testes agora rodam com `uv run pytest -q`. O `pytest -x` direto não funciona mais, porque as dependências ficam no ambiente do uv.
---
E saímos do Heroku: o deploy agora é no Fly.io, app `kizomba-api`, com `fly deploy`.
