import json
import math
import os
import re
import unicodedata
from functools import lru_cache
from .config import ROOT

PLACES = json.loads((ROOT / "data" / "places.json").read_text(encoding="utf-8"))
BY_ID = {p["id"]: p for p in PLACES}

def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")

def number(value, name, lo, hi):
    if isinstance(value, bool):
        raise ValueError(f"{name}: informe um número válido.")
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name}: informe um número válido.") from None
    if not math.isfinite(value) or not lo <= value <= hi:
        raise ValueError(f"{name}: valor deve estar entre {lo} e {hi}.")
    return value

def distance(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2-p1)/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(math.radians(lon2-lon1)/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(max(0, 1-a)))

@lru_cache(maxsize=1)
def semantic_index():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise ValueError("Modo semantic requer requirements-semantic.txt. Instale ou use RECOMMENDER=keyword.") from None
    try:
        model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"))
        vectors = model.encode([p["description"] + " " + " ".join(p["tags"]) for p in PLACES], normalize_embeddings=True)
        return model, vectors
    except Exception:
        raise ValueError("Falha ao carregar embeddings. Confira internet/modelo ou use RECOMMENDER=keyword.") from None

def search(data):
    lat = number(data.get("lat"), "Latitude", -90, 90)
    lon = number(data.get("lon"), "Longitude", -180, 180)
    radius = number(data.get("radius", 3), "Raio", 0.1, 20)
    interests = str(data.get("interests", ""))[:1000]
    mode = os.getenv("RECOMMENDER", "keyword")
    if mode not in ("keyword", "semantic"):
        raise ValueError("RECOMMENDER deve ser keyword ou semantic.")
    tokens = set(re.findall(r"\w+", normalize(interests))) - {"quero", "para", "com", "uma", "que", "dos", "das", "conhecer", "lugares", "de", "e", "o", "a"}
    similarities = None
    if mode == "semantic" and interests.strip():
        model, vectors = semantic_index()
        similarities = vectors @ model.encode(interests, normalize_embeddings=True)
    found = []
    for index, place in enumerate(PLACES):
        km = distance(lat, lon, place["lat"], place["lon"])
        if km > radius:
            continue
        words = set(re.findall(r"\w+", normalize(place["description"] + " " + " ".join(place["tags"])) ))
        overlap = sorted(tokens & words)
        relevance = float(similarities[index]) if similarities is not None else len(overlap) / max(1, len(tokens))
        score = .8 * relevance + .2 * (1 - km/radius)
        original_words = {normalize(w): w for w in re.findall(r"\w+", place["description"] + " " + " ".join(place["tags"]))}
        overlap = [original_words.get(w, w) for w in overlap]
        found.append({**place, "distance_km": round(km, 3), "score": round(score, 4),
                      "reason": "Similaridade semantica e proximidade" if similarities is not None else ("Interesses: " + ", ".join(overlap) if overlap else "Proximidade do ponto escolhido")})
    found.sort(key=lambda p: (-p["score"], p["distance_km"], p["id"]))
    return {"mode": mode, "places": found, "coordinate_status": "aproximadas", "transport_included": False}

def plan(data):
    selections = data.get("stops", [])
    if not isinstance(selections, list) or len(selections) > 10:
        raise ValueError("Escolha até dez paradas.")
    group = number(data.get("group", 1), "Pessoas", 1, 20)
    if group != int(group):
        raise ValueError("Pessoas deve ser inteiro.")
    budget = number(data.get("budget", 150), "Orcamento por pessoa", 0, 100000)
    available = number(data.get("minutes", 240), "Tempo disponível", 1, 10080)
    stops, seen = [], set()
    for item in selections:
        if not isinstance(item, dict) or item.get("id") not in BY_ID:
            raise ValueError("Parada desconhecida.")
        if item["id"] in seen:
            raise ValueError("Não repita a mesma parada.")
        seen.add(item["id"])
        place = BY_ID[item["id"]]
        duration = number(item.get("duration", place["visit_minutes"][0]), "Duração", 5, 720)
        lo = number(item.get("cost_min", place["sample_cost"][0]), "Gasto mínimo", 0, 100000)
        hi = number(item.get("cost_max", place["sample_cost"][1]), "Gasto máximo", 0, 100000)
        if lo > hi:
            raise ValueError("Gasto mínimo não pode superar o máximo.")
        stops.append({"id": place["id"], "name": place["name"], "duration": duration,
                      "cost_min": lo, "cost_max": hi, "lat": place["lat"], "lon": place["lon"]})
    total = sum(p["duration"] for p in stops)
    lo, hi = sum(p["cost_min"] for p in stops), sum(p["cost_max"] for p in stops)
    warnings = ["Custos e durações são simulações editáveis, não preços confirmados.",
                "Deslocamentos, horários de funcionamento e transporte não estão incluídos.",
                "Coordenadas aproximadas: confirme os destinos no serviço de mapas.",
                "Sem dados locais verificados para classificar segurança de ruas ou bairros."]
    if hi > budget:
        warnings.append("A faixa superior de gastos excede o orçamento por pessoa.")
    if total > available:
        warnings.append("As visitas excedem o tempo disponível, mesmo sem deslocamento.")
    return {"stops": stops, "visit_minutes": total, "cost_person": [lo, hi],
            "cost_group": [lo * group, hi * group], "budget": budget, "group": int(group),
            "available_minutes": available, "warnings": warnings, "transport_included": False,
            "budget_exceeded": hi > budget, "time_exceeded": total > available}
