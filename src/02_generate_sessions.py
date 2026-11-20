"""
Passo 2: roda cada roteiro de data/conversas/*.md como uma sessão separada.
A memória de entrada fica montada como read_only, então o agente LÊ os fatos
antigos mas não consegue corrigi-los: quem vai corrigir é o dream.

Step 2: runs each script in data/conversas/*.md as its own session.
The input memory is mounted read_only, so the agent READS the old facts but
cannot fix them: the dream will.

    python src/02_generate_sessions.py
"""

from common import (
    DATA,
    RESULTS,
    load_state,
    memory_resource,
    new_session,
    parse_conversation,
    require,
    send_and_wait,
    update_state,
    write_transcript,
)


def main() -> None:
    state = load_state()
    require(state, "agent_id", "environment_id", "input_store_id", "seed_session_id")
    sessions: dict[str, str] = state.get("sessions", {})  # nome do roteiro -> session id

    files = sorted((DATA / "conversas").glob("*.md"))
    if not files:
        raise SystemExit("Nenhum roteiro em data/conversas / no scripts found.")

    for path in files:
        name = path.stem
        if name in sessions:
            print(f"[{name}] já existe / already exists: {sessions[name]}")
            continue

        messages = parse_conversation(path)
        session = new_session(
            f"conversa: {name}",
            [memory_resource(state["input_store_id"], "read_only",
                             "Memória de longo prazo do projeto kizomba-api.")],
        )
        print(f"[{name}] sessão {session.id} — {len(messages)} mensagens")

        turns = []
        for i, msg in enumerate(messages, 1):
            reply = send_and_wait(session.id, msg)
            turns.append((msg, reply))
            print(f"  {i}/{len(messages)} ok")

        write_transcript(RESULTS / "transcripts" / f"{name}.md", name, turns)
        sessions[name] = session.id
        update_state(sessions=sessions)  # salva a cada sessão / saved after each session

    print(f"\n{len(sessions)} sessões prontas para o dream / sessions ready for the dream.")


if __name__ == "__main__":
    main()
