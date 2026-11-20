"""
Passo 4: faz as mesmas perguntas a duas sessões novas, uma com a memória de
ENTRADA e outra com a memória de SAÍDA do dream, e grava o lado a lado em
results/comparacao.md. Depois, confira com data/gabarito.md.

Step 4: asks the same questions to two fresh sessions, one mounting the INPUT
memory and one mounting the dream's OUTPUT memory, and writes a side-by-side
report to results/comparacao.md. Then check it against data/gabarito.md.

    python src/04_compare.py
"""

from datetime import datetime, timezone

from common import (
    DATA,
    RESULTS,
    load_state,
    memory_resource,
    new_session,
    read_lines,
    require,
    send_and_wait,
    update_state,
)

MOUNT_NOTE = "Memória de longo prazo do projeto kizomba-api. Consulte antes de responder."


def ask_all(label: str, store_id: str, questions: list[str]) -> tuple[str, list[str]]:
    session = new_session(f"comparacao: {label}",
                          [memory_resource(store_id, "read_only", MOUNT_NOTE)])
    print(f"[{label}] sessão {session.id}")
    answers = []
    for i, q in enumerate(questions, 1):
        answers.append(send_and_wait(session.id, q))
        print(f"  {i}/{len(questions)} ok")
    return session.id, answers


def main() -> None:
    state = load_state()
    require(state, "input_store_id", "output_store_id")
    questions = read_lines(DATA / "perguntas.md")

    in_sid, before = ask_all("ANTES / input", state["input_store_id"], questions)
    out_sid, after = ask_all("DEPOIS / output", state["output_store_id"], questions)
    update_state(compare_sessions=[in_sid, out_sid])

    lines = [
        "# Comparação antes × depois do dream / Before × after comparison",
        "",
        f"- Gerado em / generated at: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC",
        f"- Dream: `{state.get('dream_id')}`",
        "- Gabarito / answer key: [`data/gabarito.md`](../data/gabarito.md)",
        "",
    ]
    for i, (q, a, b) in enumerate(zip(questions, before, after), 1):
        lines += [
            f"## {i}. {q}",
            "",
            "### Antes (memória de entrada) / Before (input memory)",
            "",
            a,
            "",
            "### Depois (memória do dream) / After (dream output)",
            "",
            b,
            "",
            "### Avaliação / Evaluation",
            "",
            "- [ ] Bateu com o gabarito / matches the answer key",
            "- Notas / notes:",
            "",
        ]

    out = RESULTS / "comparacao.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nRelatório / report: {out.relative_to(RESULTS.parent)}")


if __name__ == "__main__":
    main()
