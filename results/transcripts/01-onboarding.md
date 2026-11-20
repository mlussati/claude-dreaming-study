# 01-onboarding

**USER:**

Oi! Comecei hoje no kizomba-api. O que você já sabe sobre o projeto?

**AGENT:**

Olá! Bem-vindo(a). A memória tem estes fatos, com data de março/2026:

- **Linguagem:** Python 3.11
- **Testes:** `pytest -x`
- **Deploy:** Heroku, app `kizomba-api-prod`, com `git push heroku main`
- **Branch principal:** `main`
- **Convenção:** type hints em todas as funções públicas

Os fatos podem estar desatualizados. Confirme o processo de deploy com a equipe antes de usá-lo.

---

**USER:**

Boa. Uma convenção que o time segue: docstrings em português, no estilo Google. E o lint é com ruff: rodamos `ruff check .` antes de todo commit.

**AGENT:**

Anotado para esta conversa:

- **Docstrings:** em português, no estilo Google.
- **Lint:** `ruff check .` antes de todo commit.

Não salvei isso na memória, porque você não pediu. Se quiser que eu registre, é só dizer.

---

**USER:**

Ah, e uma mudança: agora a gente coloca type hints em todas as funções, inclusive nas privadas, não só nas públicas.

**AGENT:**

Entendido. A convenção de type hints agora vale para todas as funções, inclusive as privadas. Isso substitui o que estava na memória, que falava só das públicas.

Ainda não gravei nada na memória. Quer que eu registre as três coisas: docstrings em português no estilo Google, `ruff check .` antes de cada commit e a nova regra de type hints?

---
