"""
Passo 2: a consolidação (o seu "dreaming").

Entrada:
  runs/local/notas_brutas/*.md   (o que o agente gravou)
  runs/local/transcricoes/*.md   (o que de fato aconteceu)

Saída:
  runs/local/notas_consolidadas/*.md   store novo (as notas brutas não são tocadas)
  runs/local/l2_entrada.md             exatamente o que o modelo recebeu
  runs/local/l2_resposta.json          resposta crua do modelo
  results/local/consolidacao.json      contagens e tokens (Q5 a/b)
  results/local/decisoes.md            por que cada nota ficou, mudou ou saiu

Decisões
--------
1. Entrada. Notas brutas E transcrições. As notas são o que será reorganizado; as
   transcrições são a fonte da verdade. As notas misturam o que o usuário disse com
   suposições do próprio agente ("presumo `uv run ruff check .`", "Heroku foi só um
   palpite"); só a transcrição permite separar uma coisa da outra. Cada nota bruta
   recebe um ID determinístico (`03#2` = sessão 03, 2ª nota) para o log poder citá-la.

2. Instruções. Partem de data/dream_instructions.md (fatos técnicos duráveis, mais
   recente vence, sem debug resolvido, em português) e viram regras numeradas R1–R5,
   para que cada decisão diga qual regra aplicou.

3. Desempate numa contradição (R1 > R2):
   R1. Só fala do USUÁRIO na transcrição conta como evidência. Fala do agente e nota
       bruta sem respaldo na transcrição não vencem nada. O seed (00) não tem
       transcrição: vale até alguma fala do usuário contradizê-lo.
   R2. Entre falas do usuário, vence a mais recente: sessão de número maior; na mesma
       sessão, a mensagem posterior. A ordem vem do nome do arquivo, não do modelo.

4. Como saber depois por que ele decidiu assim:
   - o modelo devolve JSON, não markdown solto: cada nota final traz operação, IDs de
     origem, IDs vencidos, regra aplicada e uma CITAÇÃO LITERAL da fala do usuário;
     cada nota descartada traz motivo e regra;
   - o código (não o modelo) confere: toda nota bruta precisa aparecer em algum lugar
     (cobertura: pelo menos uma vez, porque uma nota bruta pode ter vários fatos)
     e toda citação precisa existir, literalmente, numa fala do USUÁRIO
     da sessão citada. Falhas vão para decisoes.md;
   - as contagens do consolidacao.json são calculadas a partir desse log, não
     declaradas pelo modelo;
   - entrada e resposta crua ficam em runs/local/ para reproduzir a chamada.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from common_local import CONSOLIDATED, DATA, MODEL, OUT, RAW, RUNS, TRANSCRIPTS, ask

INSTRUCTIONS = """
Você consolida a memória de um agente do projeto kizomba-api. É um passo offline:
você não conversa com ninguém, só reorganiza notas.

Você recebe:
- NOTAS BRUTAS, cada uma com um ID `SS#n` (SS = sessão). O agente só acrescentava
  notas, então há duplicatas, contradições e suposições dele mesmo.
- TRANSCRIÇÕES das sessões 01..04, em ordem cronológica. A sessão 00 é a memória
  inicial e não tem transcrição.

Regras (cite o código da regra em cada decisão):
R1 Fonte. Só fala do USUÁRIO numa transcrição é evidência. Fala do AGENTE, sugestão,
   suposição, palpite ou algo "presumido"/"não confirmado" NÃO é fato: não entra na
   memória e não vence contradição. Nota do seed (00) vale até ser contradita por
   fala do usuário.
R2 Recência. Se duas informações se contradizem, vence a fala do usuário mais
   recente: sessão de número maior; na mesma sessão, a mensagem posterior. A perdedora
   sai da memória (não guarde "antes era X").
R3 Duplicata. O mesmo fato em várias notas vira UMA nota, listando todas as origens.
R4 Durável. Mantenha só fatos técnicos duráveis: versões, comandos, deploy, variáveis
   de ambiente, fluxo de branches, convenções de código, arquivos do projeto. Remova
   debug já resolvido, pendências/TODOs, planos e checklists de uma tarefa,
   contexto pessoal do usuário.
   Exceção: se um bug resolvido deu origem a uma regra que continua valendo
   (ex.: uma variável obrigatória), guarde o MOTIVO junto da regra, numa frase
   curta. O que sai é o passo a passo do debug, não a causa da regra.
   Valores ditos pelo usuário são o valor do projeto, não exemplo: escreva-os como tal.
R5 Enterrado. Fato durável dito pelo usuário que nenhuma nota registrou (ou registrou
   mal) deve ser criado/corrigido a partir da transcrição.

Escreva as notas em português, curtas, uma ideia por nota, e agrupe por arquivo
temático (ex.: stack.md, deploy.md, ambiente.md, convencoes.md, git.md).

Responda SOMENTE com um JSON válido, sem texto fora dele, neste formato:
{
  "notas": [
    {
      "arquivo": "stack.md",
      "texto": "Python 3.12, dependências gerenciadas com uv.",
      "operacao": "mantida | fundida | substituida | criada",
      "origens": ["03#1"],
      "vencidas": ["00#1"],
      "regra": "R2",
      "sessao_evidencia": "03",
      "evidencia": "trecho COPIADO LITERALMENTE de uma fala do USUÁRIO dessa sessão"
    }
  ],
  "descartadas": [
    {"id": "02#4", "regra": "R4", "motivo": "pendência de tarefa, não é fato durável"}
  ]
}

Significado de operacao:
- mantida: veio de uma única nota, sem conflito.
- fundida: junta duas ou mais notas que diziam o mesmo fato (R3).
- substituida: resolveu contradição; "vencidas" lista os IDs que perderam (R2/R1).
- criada: não estava em nenhuma nota; "origens" fica vazio (R5).
Para nota que vem só do seed, use "sessao_evidencia": "00" e "evidencia": "seed".
Todo ID de nota bruta tem de aparecer pelo menos uma vez em "origens", "vencidas" ou
"descartadas". Uma nota bruta com vários fatos pode (e deve) ser origem de cada nota
final que usa um desses fatos; se o mesmo fato aparece em várias notas brutas, liste
todas em "origens" e use "fundida". Como evidência, cite a fala do usuário que diz o
fato de forma mais explícita.
"""


# --------------------------------------------------------------------------- #
# Entrada
# --------------------------------------------------------------------------- #

def split_notes(text: str) -> list[str]:
    """Uma nota = um tópico de 1º nível ("- " ou "* "); linhas indentadas vão junto.
    Títulos e linhas soltas fora de tópico são ignorados."""
    notes: list[str] = []
    for line in text.splitlines():
        if re.match(r"^[-*] ", line):
            notes.append(line[2:].strip())
        elif notes and line.startswith((" ", "\t")) and line.strip():
            notes[-1] += "\n" + line.rstrip()
    return notes


def raw_notes() -> dict[str, str]:
    out: dict[str, str] = {}
    for p in sorted(RAW.glob("*.md")):
        sess = p.stem[:2]
        for i, n in enumerate(split_notes(p.read_text(encoding="utf-8")), 1):
            out[f"{sess}#{i}"] = n
    return out


def user_turns(path: Path) -> list[str]:
    """Falas do usuário numa transcrição gerada pelo l1."""
    parts = path.read_text(encoding="utf-8").split("\n\n---\n\n")
    return [p.split("**USER:**", 1)[1].strip() for p in parts if "**USER:**" in p]


def build_input(notes: dict[str, str]) -> str:
    lines = ["# NOTAS BRUTAS\n"]
    lines += [f"[{nid}] {txt}" for nid, txt in notes.items()]
    lines.append("\n# TRANSCRIÇÕES (ordem cronológica)\n")
    for p in sorted(TRANSCRIPTS.glob("*.md")):
        lines.append(f"## Sessão {p.stem[:2]} ({p.stem})\n")
        lines.append(p.read_text(encoding="utf-8"))
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Verificação
# --------------------------------------------------------------------------- #

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("`", "")).strip().lower()


def parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise SystemExit(f"Resposta sem JSON. Veja {RUNS / 'l2_resposta.json'}")
    return json.loads(m.group(0))


def verify(result: dict, notes: dict[str, str]) -> list[str]:
    problems: list[str] = []
    turns = {p.stem[:2]: [norm(t) for t in user_turns(p)] for p in TRANSCRIPTS.glob("*.md")}

    seen: dict[str, int] = {nid: 0 for nid in notes}
    for n in result["notas"]:
        for nid in n.get("origens", []) + n.get("vencidas", []):
            if nid not in seen:
                problems.append(f"ID inexistente citado: {nid}")
            else:
                seen[nid] += 1
        sess, ev = n.get("sessao_evidencia", ""), n.get("evidencia", "")
        if sess == "00" and ev == "seed":
            if any(not o.startswith("00#") for o in n.get("origens", [])):
                problems.append(f"Evidência 'seed' para nota com origem fora do seed: {n['texto']!r}")
        elif not any(norm(ev) in t for t in turns.get(sess, [])):
            problems.append(f"Citação não encontrada em fala do usuário da sessão {sess}: {ev!r}")
        if n.get("operacao") == "substituida" and not n.get("vencidas"):
            problems.append(f"'substituida' sem IDs vencidos: {n['texto']!r}")
    for d in result.get("descartadas", []):
        if d["id"] not in seen:
            problems.append(f"ID inexistente descartado: {d['id']}")
        else:
            seen[d["id"]] += 1
    problems += [f"Nota bruta {nid} não foi tratada" for nid, c in seen.items() if c == 0]
    return problems


# --------------------------------------------------------------------------- #
# Saída
# --------------------------------------------------------------------------- #

def write_store(result: dict) -> None:
    for old in CONSOLIDATED.glob("*.md"):
        old.unlink()
    by_file: dict[str, list[str]] = {}
    for n in result["notas"]:
        name = Path(n["arquivo"]).name
        if not name.endswith(".md"):
            name += ".md"
        by_file.setdefault(name, []).append(n["texto"])
    for name, texts in by_file.items():
        body = f"# {name[:-3]}\n\n" + "\n".join(f"- {t}" for t in texts) + "\n"
        (CONSOLIDATED / name).write_text(body, encoding="utf-8")


def write_decisions(result: dict, notes: dict[str, str], problems: list[str]) -> None:
    def cell(s: str) -> str:
        return s.replace("|", "\\|").replace("\n", " ")

    out = [
        "# Decisões da consolidação (l2)\n",
        f"Modelo: `{MODEL}`. Regras: ver `INSTRUCTIONS` em `local/l2_consolidar.py`.\n",
        "## Notas finais\n",
        "| Arquivo | Nota | Operação | Origens | Vencidas | Regra | Evidência (fala do usuário) |",
        "|---|---|---|---|---|---|---|",
    ]
    for n in result["notas"]:
        ev = n.get("evidencia", "")
        out.append(
            f"| {n['arquivo']} | {cell(n['texto'])} | {n['operacao']} | {', '.join(n.get('origens', []))} "
            f"| {', '.join(n.get('vencidas', []))} | {n.get('regra', '')} "
            f"| s{n.get('sessao_evidencia', '?')}: {cell(ev)} |"
        )
    out += ["\n## Notas descartadas\n", "| ID | Nota bruta | Regra | Motivo |", "|---|---|---|---|"]
    for d in result.get("descartadas", []):
        out.append(f"| {d['id']} | {cell(notes.get(d['id'], '?'))[:160]} | {d['regra']} | {cell(d['motivo'])} |")
    out.append("\n## Verificação automática\n")
    out += [f"- ⚠️ {p}" for p in problems] or ["- ok: todas as notas brutas tratadas e todas as citações conferem."]
    (OUT / "decisoes.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> None:
    notes = raw_notes()
    if not notes:
        raise SystemExit("Sem notas brutas. Rode o passo 1 antes.")
    user = build_input(notes)
    (RUNS / "l2_entrada.md").write_text(f"# SYSTEM\n{INSTRUCTIONS}\n\n# USER\n{user}", encoding="utf-8")

    text, usage = ask(INSTRUCTIONS, user, max_tokens=8000)
    (RUNS / "l2_resposta.json").write_text(text, encoding="utf-8")
    result = parse_json(text)

    problems = verify(result, notes)
    write_store(result)
    write_decisions(result, notes, problems)

    ops = [n["operacao"] for n in result["notas"]]
    stats = {
        "modelo": MODEL,
        "instrucoes_base": str((DATA / "dream_instructions.md").relative_to(DATA.parent)),
        "notas_antes": len(notes),
        "notas_depois": len(result["notas"]),
        "arquivos_depois": sorted(p.name for p in CONSOLIDATED.glob("*.md")),
        "mantidas": ops.count("mantida"),
        "fundidas": ops.count("fundida"),
        "substituidas": ops.count("substituida"),
        "criadas": ops.count("criada"),
        "removidas": len(result.get("descartadas", [])),
        "problemas_verificacao": len(problems),
        "tokens": usage,
    }
    (OUT / "consolidacao.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({k: v for k, v in stats.items() if k != "arquivos_depois"}, ensure_ascii=False))
    for p in problems:
        print(f"⚠️  {p}")


if __name__ == "__main__":
    main()
