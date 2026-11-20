"""
Passo 3: cria o dream (memory store de entrada + sessões) e acompanha até o fim.
Se você interromper com Ctrl+C, o dream continua no servidor; rode de novo para
retomar o acompanhamento, ou use --cancel para cancelar.

Step 3: creates the dream (input memory store + sessions) and follows it to the end.
If you stop with Ctrl+C the dream keeps running server-side; run again to resume
following it, or pass --cancel to cancel it.

    python src/03_run_dream.py
    python src/03_run_dream.py --cancel
"""

import json
import sys
import time
from datetime import datetime, timezone

from common import (
    DATA,
    DREAM_MODEL,
    POLL_SECONDS,
    RESULTS,
    client,
    load_state,
    require,
    update_state,
    usage_dict,
)

TERMINAL = {"completed", "failed", "canceled"}


def create_dream(state: dict):
    instructions = (DATA / "dream_instructions.md").read_text(encoding="utf-8").strip()
    session_ids = list(state["sessions"].values())
    dream = client.beta.dreams.create(
        inputs=[
            {"type": "memory_store", "memory_store_id": state["input_store_id"]},
            {"type": "sessions", "session_ids": session_ids},
        ],
        model=DREAM_MODEL,
        instructions=instructions,
    )
    update_state(dream_id=dream.id, dream_started_at=datetime.now(timezone.utc).isoformat())
    print(f"Dream criado / created: {dream.id} ({len(session_ids)} sessões, modelo {DREAM_MODEL})")
    return dream


def follow(dream):
    start = time.monotonic()
    last = None
    while dream.status not in TERMINAL:
        time.sleep(max(POLL_SECONDS, 10))
        dream = client.beta.dreams.retrieve(dream.id)
        line = f"status={dream.status} input_tokens={dream.usage.input_tokens}"
        if line != last:
            extra = f" session={dream.session_id}" if dream.session_id else ""
            print(f"[{int(time.monotonic() - start):>5}s] {line}{extra}")
            last = line
    return dream


def main() -> None:
    state = load_state()

    if "--cancel" in sys.argv:
        require(state, "dream_id")
        client.beta.dreams.cancel(state["dream_id"])
        print(f"Dream {state['dream_id']} cancelado / canceled.")
        return

    require(state, "input_store_id", "sessions")

    if state.get("dream_id"):
        dream = client.beta.dreams.retrieve(state["dream_id"])
        print(f"Retomando / resuming {dream.id} (status={dream.status})")
    else:
        dream = create_dream(state)

    try:
        dream = follow(dream)
    except KeyboardInterrupt:
        print("\nO dream continua no servidor. Rode de novo para retomar ou use --cancel.")
        print("The dream keeps running server-side. Run again to resume or pass --cancel.")
        return

    output_store_id = next(
        (o.memory_store_id for o in dream.outputs if o.type == "memory_store"), None
    )
    if output_store_id:
        update_state(output_store_id=output_store_id)

    summary = {
        "dream_id": dream.id,
        "status": dream.status,
        "model": DREAM_MODEL,
        "input_store_id": state["input_store_id"],
        "output_store_id": output_store_id,
        "sessions": len(state["sessions"]),
        "created_at": str(dream.created_at),
        "ended_at": str(dream.ended_at),
        "usage": usage_dict(dream.usage),
        "error": usage_dict(dream.error) if dream.error else None,
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "dream.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                                        encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if dream.status != "completed":
        raise SystemExit(f"Dream terminou como {dream.status}. Veja `error` acima.")
    print(f"\nPronto. Store de saída / output store: {output_store_id}")


if __name__ == "__main__":
    main()
