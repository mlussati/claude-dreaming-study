"""
Lab local, sem a API de Dreams: só a Messages API.
Local lab without the Dreams API: plain Messages API only.

Saídas em runs/local/ (ignorado pelo git) e results/local/ (vai para o commit).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from common import DATA, RESULTS, ROOT, client  # noqa: E402

MODEL = os.getenv("MODEL", "claude-sonnet-5-5")

RUNS = ROOT / "runs" / "local"
RAW = RUNS / "notas_brutas"          # um arquivo de nota por sessão
CONSOLIDATED = RUNS / "notas_consolidadas"
TRANSCRIPTS = RUNS / "transcricoes"
OUT = RESULTS / "local"

for d in (RAW, CONSOLIDATED, TRANSCRIPTS, OUT):
    d.mkdir(parents=True, exist_ok=True)


def ask(system: str, user: str, max_tokens: int = 2000) -> tuple[str, dict]:
    """Uma chamada simples. Devolve texto e uso de tokens."""
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    usage = {"input": resp.usage.input_tokens, "output": resp.usage.output_tokens}
    return text, usage


def read_dir(d: Path) -> str:
    """Junta todos os .md de uma pasta, com o nome do arquivo como cabeçalho."""
    parts = [f"## {p.name}\n{p.read_text(encoding='utf-8')}" for p in sorted(d.glob("*.md"))]
    return "\n\n".join(parts)


def conversations() -> list[Path]:
    return sorted((DATA / "conversas").glob("*.md"))


def user_messages(path: Path) -> list[str]:
    """Mensagens do usuário: o arquivo separa mensagens com '---' e começa com comentários HTML."""
    text = "\n".join(l for l in path.read_text(encoding="utf-8").splitlines() if not l.startswith("<!--"))
    return [m.strip() for m in text.split("\n---\n") if m.strip()]
