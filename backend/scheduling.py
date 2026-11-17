"""Cronograma heurístico editável: um desenvolvedor, tarefas sequenciais."""
import math
from datetime import date, datetime, timedelta, timezone
from .tourism import number

def workday(value):
    while value.weekday() >= 5:
        value += timedelta(days=1)
    return value

def offset(start, days):
    day = workday(start)
    for _ in range(days):
        day = workday(day + timedelta(days=1))
    return day

def make(record, options=None):
    options = options or {}
    if not isinstance(options, dict):
        raise ValueError("Configuração de prazos inválida.")
    today = datetime.now(timezone(timedelta(hours=-3))).date()
    try:
        start = date.fromisoformat(options.get("start_date", today.isoformat()))
    except (ValueError, TypeError):
        raise ValueError("Informe uma data inicial válida.") from None
    if not 2020 <= start.year <= 2100:
        raise ValueError("Ano inicial deve estar entre 2020 e 2100.")
    start = workday(start)
    hours_day = number(options.get("hours_day", 6), "Horas por dia", 1, 12)
    complexity = options.get("complexity", "medium")
    if complexity not in ("low", "medium", "high"):
        raise ValueError("Complexidade deve ser low, medium ou high.")
    scale = {"low": 0.5, "medium": 1, "high": 2}[complexity]
    tasks = record["plan"]["tasks"]
    known_ids = {t["id"] for t in tasks}
    overrides = options.get("overrides", [])
    if not isinstance(overrides, list) or len(overrides) > len(tasks):
        raise ValueError("Estimativas de tarefas inválidas.")
    mapped = {}
    for item in overrides:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or item["id"] not in known_ids or item["id"] in mapped:
            raise ValueError("Estimativa contém tarefa desconhecida ou repetida.")
        lo = number(item.get("min_hours"), "Horas mínimas", 0.5, 1000)
        hi = number(item.get("max_hours"), "Horas máximas", 0.5, 1000)
        if lo > hi:
            raise ValueError("Horas mínimas não podem superar as máximas.")
        mapped[item["id"]] = (lo,hi)
    rows = []
    def add(identifier, title, low, high, dependency, kind):
        min_so_far = sum(r["min_hours"] for r in rows)
        max_so_far = sum(r["max_hours"] for r in rows)
        rows.append({"id": identifier, "title": title, "min_hours": low, "max_hours": high,
                     "depends_on": dependency, "kind": kind,
                     "start_early": offset(start, math.floor(min_so_far/hours_day)).isoformat(),
                     "finish_early": offset(start, max(0, math.ceil((min_so_far+low)/hours_day)-1)).isoformat(),
                     "start_late": offset(start, math.floor(max_so_far/hours_day)).isoformat(),
                     "finish_late": offset(start, max(0, math.ceil((max_so_far+high)/hours_day)-1)).isoformat()})
    add("PREP", "Descoberta, requisitos e desenho da solução", 2*scale, 4*scale, None, "phase")
    for task in tasks:
        lo, hi = mapped.get(task["id"], (4*scale, 8*scale))
        add("TASK:"+task["id"], task["title"], lo, hi, rows[-1]["id"], "task")
        rows[-1]["task_id"] = task["id"]
        rows[-1]["requirement_id"] = task["requirement_id"]
    low = sum(r["min_hours"] for r in rows)
    high = sum(r["max_hours"] for r in rows)
    add("QA", "Integração, testes e revisão dos critérios", max(1,round(low*.2,1)), max(2,round(high*.25,1)), rows[-1]["id"], "phase")
    add("DELIVERY", "Documentação e preparação da entrega", 1*scale, 2*scale, rows[-1]["id"], "phase")
    minimum,maximum = sum(r["min_hours"] for r in rows),sum(r["max_hours"] for r in rows)
    return {"record_id": record["id"], "start_date": start.isoformat(), "hours_day": hours_day, "complexity": complexity,
            "rows": rows, "min_hours": round(minimum,1), "max_hours": round(maximum,1),
            "min_workdays": math.ceil(minimum/hours_day), "max_workdays": math.ceil(maximum/hours_day),
            "finish_early": rows[-1]["finish_early"], "finish_late": rows[-1]["finish_late"],
            "assumptions": ["Estimativa heurística, não uma promessa de prazo ou previsão treinada com projetos reais.",
                            "Uma pessoa, tarefas sequenciais, segunda a sexta, sem descontar feriados.",
                            "Cada tarefa depende da anterior como hipótese de planejamento; não é uma dependência descoberta automaticamente.",
                            "Padrão por tarefa: 4–8 h em complexidade média; baixa multiplica por 0,5 e alta por 2.",
                            "Inclui descoberta, margem para integração/testes e documentação; revise esforço e escopo.",
                            "As alterações de prazo são locais à sessão até exportar; não alteram as versões de requisitos."]}
