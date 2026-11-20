# 02-bug-fuso-horario

**USER:**

Estou com um bug: os horários das reservas aparecem 1 hora adiantados. O log mostra `2026-04-02T15:00:00+00:00` para uma reserva marcada às 14h.

**AGENT:**

Não há nada na memória sobre fuso horário, então isto vem de raciocínio geral.

**O que o log indica:** `15:00+00:00` é 1 hora a mais do que as 14h marcadas, tratadas como UTC. Isso sugere uma conversão de fuso feita com o sinal errado, ou um horário de verão aplicado duas vezes. Se o fuso local fosse UTC+1 (Angola ou Lisboa no verão), o valor correto em UTC seria `13:00+00:00`.

**Verificações, nesta ordem:**
1. **Datetime sem fuso:** procure `datetime.now()`, `datetime.utcnow()` e `datetime.fromisoformat()` sem tzinfo. Use `datetime.now(timezone.utc)` ou `zoneinfo.ZoneInfo("...")`.
2. **Offset fixo:** procure `timedelta(hours=...)` somado ou subtraído à mão. Troque por `.astimezone(ZoneInfo(...))`.
3. **`pytz`:** veja se há `datetime(..., tzinfo=pytz.timezone(...))`. Isso gera offsets errados, como LMT. O certo é `tz.localize(...)`, ou migrar para `zoneinfo` (Python 3.11).
4. **Conversão dupla:** veja se o horário é convertido para UTC no input e de novo na serialização.
5. **Fuso do servidor:** no Heroku o servidor roda em UTC, e o banco pode ter `timestamp without time zone`.
6. **Teste de regressão:** reserva às 14h no fuso do negócio, em data com e sem horário de verão.

Para eu apontar a linha exata, me diga:
- Qual é o fuso esperado do negócio?
- Como a reserva é recebida: string, com ou sem offset?
- Onde fica o código que cria ou serializa o horário?

---

**USER:**

Achei. O servidor estava em UTC. Resolvi definindo `KIZOMBA_TZ=Africa/Luanda` no `.env`; essa variável é obrigatória em todo ambiente, inclusive no CI. O print de debug que coloquei em `reservas.py`, linha 88, eu já apaguei.

**AGENT:**

Que bom que achou. Dois pontos para conferir:

- **Heroku:** o `.env` normalmente não é lido lá. Defina também com `heroku config:set KIZOMBA_TZ=Africa/Luanda -a kizomba-api-prod`.
- **CI:** como a variável é obrigatória, coloque-a nas variáveis ou secrets do pipeline. O ideal é o código falhar na inicialização se ela estiver ausente, em vez de cair em UTC sem avisar.

`Africa/Luanda` é UTC+1 o ano todo, sem horário de verão. Por isso 14h local vira `13:00+00:00` em UTC. Vale um teste de regressão que confirme isso.

Quer que eu registre na memória a regra da `KIZOMBA_TZ` e a causa do bug? Só escrevo lá se você pedir.

---

**USER:**

Valeu. Só para fechar: lembra que no time tudo tem que ser tipado, ok?

**AGENT:**

Lembro, sim. A memória do projeto registra a convenção de type hints em todas as funções públicas. Vou seguir isso em qualquer código que eu sugerir, por exemplo:

```python
def get_tz() -> ZoneInfo: ...
```

---
