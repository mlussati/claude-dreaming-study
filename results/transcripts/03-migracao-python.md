# 03-migracao-python

**USER:**

Novidade: semana passada migramos o kizomba-api para Python 3.12 e trocamos o pip pelo uv.

**AGENT:**

Anotado: o kizomba-api agora usa Python 3.12 e uv no lugar do pip.

Minha memória ainda diz Python 3.11. Ela também não menciona pip, então nada sobre gerenciador de pacotes ficou desatualizado. Não escrevi nada nela, porque o combinado é só escrever quando você pedir. Se quiser, atualizo o registro.

Dois itens da memória podem ter mudado com a migração: o comando de testes (`pytest -x`) e o deploy no Heroku. Se mudaram, me diga como ficaram.

---

**USER:**

Os testes agora rodam com `uv run pytest -q`. O `pytest -x` direto não funciona mais, porque as dependências ficam no ambiente do uv.

**AGENT:**

Entendido: os testes agora rodam com `uv run pytest -q`, e o `pytest -x` direto não funciona mais.

Não gravei na memória, porque você ainda não pediu. O registro continua com `pytest -x` e Python 3.11. Se quiser, atualizo os dois itens, junto com a migração para uv.

Falta saber se o deploy no Heroku (`git push heroku main`) mudou.

---

**USER:**

E saímos do Heroku: o deploy agora é no Fly.io, app `kizomba-api`, com `fly deploy`.

**AGENT:**

Anotado: o deploy agora é no Fly.io, app `kizomba-api`, com `fly deploy`. Isso substitui o Heroku (`kizomba-api-prod`, `git push heroku main`).

Ainda não gravei nada na memória, porque você não pediu. Além disso, o store `kizomba-memoria-input` está montado como somente leitura, então a gravação talvez nem funcione nele.

Três itens estão desatualizados no registro:
- Python 3.11, que agora é 3.12 com uv no lugar do pip.
- `pytest -x`, que agora é `uv run pytest -q`.
- Deploy no Heroku, que agora é Fly.io.

Se quiser que eu registre, é só pedir.

---
