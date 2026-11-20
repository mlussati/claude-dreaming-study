# 04-release-0-4-0

**USER:**

Vamos preparar a release 0.4.0. Mudamos o fluxo de branches: o desenvolvimento agora acontece na `develop`, e a `main` só recebe tags de release.

**AGENT:**

Pela memória, o projeto usa Python 3.11 e roda os testes com `pytest -x`. O deploy é no Heroku (`kizomba-api-prod`) com `git push heroku main`, e há a convenção de type hints nas funções públicas.

O fluxo novo muda a parte do deploy. A memória ainda trata a `main` como branch principal. Com o novo fluxo, o `git push heroku main` só deve rodar depois que a `main` receber a tag de release.

Sugestão de passos para a 0.4.0:

1. Na `develop`, rodar `pytest -x` e conferir se os type hints estão nas funções públicas.
2. Atualizar a versão para 0.4.0 e o changelog na `develop`.
3. Fazer o merge da `develop` na `main`, de preferência com `--no-ff`.
4. Criar a tag `v0.4.0` na `main` e dar push da `main` e da tag.
5. Fazer o deploy com `git push heroku main`.

Perguntas:
- O deploy no Heroku continua manual, ou deve ser disparado pela tag?
- Quer que eu registre o novo fluxo de branches na memória? Só escrevo se você pedir.

---

**USER:**

O changelog fica em `CHANGELOG.md`, no formato Keep a Changelog. Pode me montar um checklist curto para essa release, usando o que você sabe do projeto?

**AGENT:**

**Checklist da release 0.4.0**

**Na `develop`**
- [ ] `pytest -x` passa.
- [ ] As funções públicas novas ou alteradas têm type hints.
- [ ] No `CHANGELOG.md` (Keep a Changelog), mover o conteúdo de `[Unreleased]` para `[0.4.0] - AAAA-MM-DD`. Usar as seções Added, Changed, Fixed, Removed e deixar um `[Unreleased]` vazio no topo.
- [ ] Atualizar os links de comparação no rodapé do changelog: `[Unreleased]` aponta para `v0.4.0...develop` e `[0.4.0]` para `v0.3.x...v0.4.0`.
- [ ] Atualizar a versão no código ou na configuração. Não sei onde ela fica no projeto.
- [ ] Registrar no changelog, em Changed, a mudança do fluxo de branches (`develop` para desenvolvimento e `main` só com tags de release).
- [ ] Fazer o commit na `develop`, por exemplo `chore: release 0.4.0`.

**Na `main`**
- [ ] Fazer o merge da `develop` na `main`, de preferência com `--no-ff`.
- [ ] Criar a tag anotada `v0.4.0` e dar push da `main` e da tag.

**Deploy**
- [ ] Rodar `git push heroku main`, no app `kizomba-api-prod`. Confirme se o deploy ainda é manual.
- [ ] Verificar os logs e o funcionamento do app depois do deploy.

**Depois**
- [ ] Se houver CI ou documentação que mencione a `main` como branch de desenvolvimento, apontar para a `develop`.

Quer que eu registre o novo fluxo de branches na memória?

---
