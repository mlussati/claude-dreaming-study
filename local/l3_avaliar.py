"""
Passo 3: faz as perguntas de data/perguntas.md com as notas brutas e com as consolidadas.

Saída: results/local/avaliacao.md, com as respostas lado a lado e uma coluna
de nota VAZIA. Você corrige à mão contra data/gabarito.md.
"""

from common_local import CONSOLIDATED, DATA, OUT, RAW, ask, read_dir

SYSTEM = (
    "Responda só com base nas notas de memória abaixo. Se a resposta não estiver nelas, diga "
    "'não está na memória'.\n\n# Notas de memória\n{notas}"
)


def questions() -> list[str]:
    lines = (DATA / "perguntas.md").read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith("#")]


def main() -> None:
    stores = {"brutas": read_dir(RAW), "consolidadas": read_dir(CONSOLIDATED)}
    if not stores["consolidadas"]:
        raise SystemExit("Sem notas consolidadas. Rode o passo 2 antes.")

    out = ["# Avaliação: notas brutas × consolidadas\n", "Corrija cada resposta contra data/gabarito.md (certo / parcial / errado).\n"]
    for i, q in enumerate(questions(), 1):
        out.append(f"## {i}. {q}\n")
        for name, notas in stores.items():
            answer, _ = ask(SYSTEM.format(notas=notas), q, max_tokens=800)
            out.append(f"**{name}:**\n\n{answer}\n\n**Nota ({name}):** \n")
    (OUT / "avaliacao.md").write_text("\n".join(out), encoding="utf-8")
    print(f"ok: {OUT / 'avaliacao.md'}")


if __name__ == "__main__":
    main()
