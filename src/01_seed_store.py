"""
Passo 1: cria o ambiente, o agente e o memory store de entrada, e grava nele
os fatos INICIAIS (e propositalmente desatualizados) do projeto fictício.

Step 1: creates the environment, the agent and the input memory store, then
writes the project's INITIAL (deliberately outdated) facts into it.

    python src/01_seed_store.py
"""

from common import (
    DATA,
    MODEL,
    NO_NETWORK,
    PROJECT_TAG,
    RESULTS,
    client,
    load_state,
    memory_resource,
    new_session,
    send_and_wait,
    toolset,
    update_state,
    write_transcript,
)

SYSTEM_PROMPT = """\
Você é o assistente técnico do projeto fictício kizomba-api (uma API de reservas).
Sua memória de longo prazo está montada em /mnt/memory. No início de cada
conversa, use glob e read para consultar o que já sabe.
Só escreva na memória quando o usuário pedir explicitamente.
Responda em português, de forma curta e objetiva."""


def setup() -> dict:
    state = load_state()

    if not state.get("environment_id"):
        env = client.beta.environments.create(
            name="estudo-dreaming",
            config={"type": "cloud", "networking": NO_NETWORK},
        )
        state = update_state(environment_id=env.id)
        print(f"Environment: {env.id}")

    if not state.get("agent_id"):
        agent = client.beta.agents.create(
            name="kizomba-assistente",
            model=MODEL,
            system=SYSTEM_PROMPT,
            # write/edit são usados só no seed; nas outras sessões a memória é read_only
            # write/edit are only used for seeding; other sessions mount memory read_only
            tools=toolset("read", "write", "edit", "glob", "grep"),
            metadata=PROJECT_TAG,
        )
        state = update_state(agent_id=agent.id)
        print(f"Agent: {agent.id}")

    if not state.get("input_store_id"):
        store = client.beta.memory_stores.create(
            name="kizomba-memoria-input",
            description="Memória inicial do projeto fictício kizomba-api (estudo de Dreams).",
        )
        state = update_state(input_store_id=store.id)
        print(f"Memory store (input): {store.id}")

    return state


def seed(state: dict) -> None:
    if state.get("seed_session_id"):
        print("Memória já semeada / memory already seeded. Pulando / skipping.")
        return

    facts = (DATA / "memoria_inicial.md").read_text(encoding="utf-8")
    session = new_session(
        "seed: memória inicial",
        [memory_resource(state["input_store_id"], "read_write",
                         "Memória de longo prazo do projeto kizomba-api.")],
    )
    print(f"Sessão de seed / seed session: {session.id}")

    turns = []
    msg1 = (
        "Salve na sua memória de longo prazo os fatos abaixo, exatamente como estão, "
        "organizados em um ou mais arquivos Markdown. Não invente nada.\n\n" + facts
    )
    turns.append((msg1, send_and_wait(session.id, msg1)))

    msg2 = "Liste os arquivos que existem agora na sua memória e mostre o conteúdo de cada um."
    reply = send_and_wait(session.id, msg2)
    turns.append((msg2, reply))

    write_transcript(RESULTS / "transcripts" / "00-seed.md", "Seed da memória inicial", turns)
    # A sessão de seed NÃO entra no dream: ela só prepara o estado inicial.
    # The seed session is NOT a dream input: it only prepares the initial state.
    update_state(seed_session_id=session.id)
    print("\nMemória inicial / initial memory:\n")
    print(reply)


if __name__ == "__main__":
    seed(setup())
