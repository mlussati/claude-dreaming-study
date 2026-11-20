"""
Passo 1: o agente de brinquedo trabalha sessão por sessão e grava notas.

Regra do agente: só ACRESCENTA (append-only). Nunca edita nem apaga nota antiga.
É isso que produz duplicata e contradição, como acontece com escrita local e incremental.

Saída:
  runs/local/notas_brutas/00-seed.md, 01-....md, ...
  runs/local/transcricoes/01-....md, ...
"""

from common_local import DATA, RAW, TRANSCRIPTS, ask, conversations, read_dir, user_messages

AGENT_SYSTEM = (
    "Você é um assistente do projeto kizomba-api. Responda ao usuário de forma curta. "
    "Use as notas de memória abaixo como contexto.\n\n# Notas de memória\n{notas}"
)

NOTE_SYSTEM = (
    "Você acabou de terminar uma sessão de trabalho. Escreva notas curtas, em tópicos, "
    "com o que vale lembrar em sessões futuras. Escreva só as notas novas desta sessão; "
    "não reescreva notas antigas."
)


def main() -> None:
    (RAW / "00-seed.md").write_text((DATA / "memoria_inicial.md").read_text(encoding="utf-8"), encoding="utf-8")

    for conv in conversations():
        notas = read_dir(RAW)
        history: list[str] = []
        for msg in user_messages(conv):
            history.append(f"**USER:**\n\n{msg}")
            reply, _ = ask(AGENT_SYSTEM.format(notas=notas), "\n\n".join(history))
            history.append(f"**AGENT:**\n\n{reply}")

        transcript = f"# {conv.stem}\n\n" + "\n\n---\n\n".join(history)
        (TRANSCRIPTS / conv.name).write_text(transcript, encoding="utf-8")

        new_notes, _ = ask(NOTE_SYSTEM, transcript)
        (RAW / conv.name).write_text(new_notes, encoding="utf-8")
        print(f"ok {conv.stem}: {len(new_notes.splitlines())} linhas de nota")


if __name__ == "__main__":
    main()
