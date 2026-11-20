<!-- Testa: detalhe ENTERRADO (KIZOMBA_TZ), RUÍDO de debug (print na linha 88) e DUPLICATA (tipagem). -->
<!-- Tests: a BURIED detail (KIZOMBA_TZ), debug NOISE (print on line 88) and a DUPLICATE (typing). -->
Estou com um bug: os horários das reservas aparecem 1 hora adiantados. O log mostra `2026-04-02T15:00:00+00:00` para uma reserva marcada às 14h.
---
Achei. O servidor estava em UTC. Resolvi definindo `KIZOMBA_TZ=Africa/Luanda` no `.env`; essa variável é obrigatória em todo ambiente, inclusive no CI. O print de debug que coloquei em `reservas.py`, linha 88, eu já apaguei.
---
Valeu. Só para fechar: lembra que no time tudo tem que ser tipado, ok?
