"""
Utilitários compartilhados pelos scripts.
Shared helpers used by every script.

Os scripts guardam os IDs que criam em `state.json` (fora do git), então cada
passo pode ser rodado de novo sem duplicar recursos.
Scripts keep the IDs they create in `state.json` (git-ignored), so each step can
be re-run without creating duplicates.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
STATE_FILE = ROOT / "state.json"

load_dotenv(ROOT / ".env")

MODEL = os.getenv("MODEL", "claude-sonnet-5-5")
DREAM_MODEL = os.getenv("DREAM_MODEL", "claude-sonnet-5-5")
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "5"))

# Usa ANTHROPIC_API_KEY do .env / Uses ANTHROPIC_API_KEY from .env
client = anthropic.Anthropic()

PROJECT_TAG = {"projeto": "claude-dreaming-study"}


# --------------------------------------------------------------------------- #
# Estado local / Local state
# --------------------------------------------------------------------------- #
def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def update_state(**values) -> dict:
    state = load_state()
    state.update(values)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state


def require(state: dict, *keys: str) -> None:
    missing = [k for k in keys if not state.get(k)]
    if missing:
        raise SystemExit(
            f"Faltando em state.json: {missing}. Rode os passos anteriores primeiro.\n"
            f"Missing from state.json: {missing}. Run the previous steps first."
        )


# --------------------------------------------------------------------------- #
# Configuração de agentes / Agent configuration
# --------------------------------------------------------------------------- #
def toolset(*names: str) -> list[dict]:
    """Todas as ferramentas desligadas, exceto as nomeadas.
    Every tool off except the ones named (pattern from the Anthropic cookbook)."""
    return [
        {
            "type": "agent_toolset_20260401",
            "default_config": {"enabled": False, "permission_policy": {"type": "auto"}},
            "configs": [{"name": n, "enabled": True} for n in names],
        }
    ]


# Sandbox sem rede / Sandbox with no network access
NO_NETWORK = {
    "type": "limited",
    "allowed_hosts": [],
    "allow_package_managers": False,
    "allow_mcp_servers": False,
}


def memory_resource(store_id: str, access: str, instructions: str) -> dict:
    return {
        "type": "memory_store",
        "memory_store_id": store_id,
        "access": access,  # "read_only" | "read_write"
        "instructions": instructions,
    }


def new_session(title: str, resources: list[dict]):
    state = load_state()
    require(state, "agent_id", "environment_id")
    return client.beta.sessions.create(
        agent=state["agent_id"],
        environment_id=state["environment_id"],
        title=title,
        resources=resources,
    )


# --------------------------------------------------------------------------- #
# Conversa / Conversation
# --------------------------------------------------------------------------- #
def _agent_messages(session_id: str) -> list[str]:
    """Textos das mensagens do agente, em ordem.
    Agent message texts, in order.

    ATENÇÃO / NOTE: o tipo de evento "agent.message" e o formato do `content`
    seguem a doc de sessions; confira se mudou.
    The "agent.message" event type and `content` shape follow the sessions docs;
    check whether they changed.
    """
    texts: list[str] = []
    for event in client.beta.sessions.events.list(session_id, order="asc"):
        if getattr(event, "type", "") != "agent.message":
            continue
        parts = [getattr(b, "text", "") for b in (getattr(event, "content", None) or [])]
        text = "".join(p for p in parts if p).strip()
        if text:
            texts.append(text)
    return texts


def send_and_wait(session_id: str, text: str, timeout: float = 900) -> str:
    """Envia uma mensagem e espera o agente terminar o turno.
    Sends one message and waits for the agent to finish its turn."""
    before = len(_agent_messages(session_id))
    client.beta.sessions.events.send(
        session_id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": text}]}],
    )
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        time.sleep(POLL_SECONDS)
        status = client.beta.sessions.retrieve(session_id).status
        if status == "terminated":
            raise RuntimeError(f"Sessão {session_id} terminou / session terminated")
        if status == "idle":
            msgs = _agent_messages(session_id)
            if len(msgs) > before:  # o turno novo terminou / the new turn is done
                return "\n\n".join(msgs[before:])
    raise TimeoutError(f"Sem resposta em {timeout}s / no reply within {timeout}s ({session_id})")


def parse_conversation(path: Path) -> list[str]:
    """Um arquivo .md = uma sessão; mensagens separadas por uma linha `---`.
    Ignora linhas que começam com `<!--` (comentários para quem lê o repo).
    One .md file = one session; messages separated by a `---` line.
    Lines starting with `<!--` are skipped (notes for repo readers)."""
    messages, current = [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("<!--"):
            continue
        if line.strip() == "---":
            if "".join(current).strip():
                messages.append("\n".join(current).strip())
            current = []
        else:
            current.append(line)
    if "".join(current).strip():
        messages.append("\n".join(current).strip())
    return messages


def write_transcript(path: Path, title: str, turns: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", ""]
    for user, agent in turns:
        lines += ["**USER:**", "", user, "", "**AGENT:**", "", agent, "", "---", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def read_lines(path: Path) -> list[str]:
    """Linhas não vazias, ignorando comentários `#`. / Non-empty lines, skipping `#` comments."""
    return [
        ln.strip()
        for ln in path.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]


def usage_dict(usage) -> dict:
    if usage is None:
        return {}
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    return dict(usage)
