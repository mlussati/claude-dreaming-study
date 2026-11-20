"""
Passo final: apaga/arquiva tudo o que o estudo criou na sua conta.
Final step: deletes/archives everything the study created in your account.

    python src/99_cleanup.py               # apaga tudo / removes everything
    python src/99_cleanup.py --keep-output # mantém o store de saída / keeps the output store

ATENÇÃO / NOTE: `dreams.archive` e `memory_stores.delete` estão na doc.
Os métodos de delete/archive de sessions, agents e environments seguem o mesmo
padrão do SDK, mas confira os nomes na doc se algum falhar.
`dreams.archive` and `memory_stores.delete` are in the docs. The delete/archive
methods for sessions, agents and environments follow the same SDK pattern, but
check their names in the docs if any of them fails.
"""

import sys

from common import STATE_FILE, client, load_state


def attempt(label: str, fn, *args) -> bool:
    try:
        fn(*args)
        print(f"ok    {label}")
        return True
    except Exception as exc:  # noqa: BLE001 — limpeza é best-effort / cleanup is best-effort
        print(f"FALHA {label}: {exc}")
        return False


def main() -> None:
    state = load_state()
    if not state:
        print("Nada para limpar / nothing to clean up.")
        return
    keep_output = "--keep-output" in sys.argv
    b = client.beta
    ok = True

    if state.get("dream_id"):
        ok &= attempt(f"dream {state['dream_id']} (archive)", b.dreams.archive, state["dream_id"])

    session_ids = [state.get("seed_session_id"), *state.get("sessions", {}).values(),
                   *state.get("compare_sessions", [])]
    for sid in filter(None, session_ids):
        ok &= attempt(f"session {sid} (delete)", b.sessions.delete, sid)

    stores = [state.get("input_store_id")]
    if not keep_output:
        stores.append(state.get("output_store_id"))
    for store_id in filter(None, stores):
        ok &= attempt(f"memory store {store_id} (delete)", b.memory_stores.delete, store_id)

    if state.get("agent_id"):
        ok &= attempt(f"agent {state['agent_id']} (archive)", b.agents.archive, state["agent_id"])
    if state.get("environment_id"):
        ok &= attempt(f"environment {state['environment_id']} (archive)",
                      b.environments.archive, state["environment_id"])

    if ok:
        STATE_FILE.unlink(missing_ok=True)
        print("\nLimpo. state.json removido / clean. state.json removed.")
    else:
        print("\nAlgo falhou; state.json mantido para você tentar de novo.")
        print("Something failed; state.json kept so you can retry.")


if __name__ == "__main__":
    main()
