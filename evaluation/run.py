"""Avaliacao pequena de recuperacao. python evaluation/run.py."""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.tourism import search
from backend.brief import generate

def main():
    root = Path(__file__).resolve().parent
    cases = json.loads((root / "cases.json").read_text(encoding="utf-8"))
    rows = []
    for case in cases:
        start = time.perf_counter()
        result = search({"lat": -14.8004, "lon": -39.0331, "radius": 3, "interests": case["query"]})
        ids = [p["id"] for p in result["places"][:3]]
        relevant = set(case["relevant"])
        recall = len(set(ids) & relevant) / len(relevant)
        rank = next((i+1 for i, identifier in enumerate(ids) if identifier in relevant), None)
        rows.append({"query": case["query"], "top3": ids, "recall_at_3": recall,
                     "reciprocal_rank_at_3": 1/rank if rank else 0, "latency_ms": round((time.perf_counter()-start)*1000, 3), "mode": result["mode"]})
    brief_rows = []
    for idea in ["Sistema de reservas para pousada", "Gestao de estoque de produtos", "Planejador de roteiro de turismo", "Kanban de tarefas pessoais", "Gestao de chamados de atendimento"]:
        p, mode = generate({"idea": idea, "audience": "Equipe pequena", "deadline": "1 semana", "technologies": "Python", "constraints": "Sem pagamentos"})
        brief_rows.append({"idea": idea, "mode": mode, "structural_validation": True, "tasks": len(p["tasks"])})
    report = {"created_at": datetime.now(timezone.utc).isoformat(), "scope": "Casos curados com a mesma base da demonstracao; nao e teste independente nem benchmark de producao.",
              "recommender": os.getenv("RECOMMENDER", "keyword"), "mean_recall_at_3": sum(r["recall_at_3"] for r in rows)/len(rows),
              "mrr_at_3": sum(r["reciprocal_rank_at_3"] for r in rows)/len(rows), "tourism_cases": rows, "brief_cases": brief_rows,
              "brief_limit": "Somente validacao estrutural do template, nao avaliacao de qualidade de uma LLM."}
    (root / "results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"mode": report["recommender"], "recall@3": report["mean_recall_at_3"], "MRR@3": report["mrr_at_3"], "report": str(root / "results.json")}, ensure_ascii=False))

if __name__ == "__main__": main()
