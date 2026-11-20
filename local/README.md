# Lab local (sem a API de Dreams)

O Dreams precisa de liberação de acesso. Este lab testa a **ideia** do dreaming com a Messages API: um agente grava notas só acrescentando, sessão a sessão, e depois uma passada offline consolida as notas.

Ele não testa o produto Dreams da Anthropic.

```bash
source .venv/bin/activate
python local/l1_notas_brutas.py   # agente de brinquedo + notas brutas + transcrições
python local/l2_consolidar.py     # a sua consolidação (você escreve)
python local/l3_avaliar.py        # perguntas com brutas × consolidadas
```

Corrija `results/local/avaliacao.md` à mão, contra `data/gabarito.md`, e faça commit de `results/local/`.
