"""Rotas reais OSRM/FOSSGIS. Sem substituir falhas por linhas retas."""
import json
import math
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from .tourism import number, plan

PROFILES = {"foot": ("routed-foot", "A pé"), "car": ("routed-car", "Carro"), "bike": ("routed-bike", "Bicicleta")}
_cache = {}
_lock = threading.Lock()
_last_request = 0.0

class RouteError(Exception):
    pass

def _fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "CacauTrip-Portfolio/2.0 (local educational prototype)", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            raw = response.read(3_000_001)
        if len(raw) > 3_000_000:
            raise RouteError("O serviço retornou uma rota muito grande.")
        return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raise RouteError(f"Serviço de rotas indisponível (HTTP {exc.code}). Tente novamente mais tarde.") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise RouteError("Não foi possível consultar as ruas. Confira a internet e tente novamente. Nenhuma rota foi inventada.") from None
    except (ValueError, UnicodeError):
        raise RouteError("O serviço de rotas retornou uma resposta inválida.") from None

def _metric(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise RouteError("Distância ou duração inválida na resposta de rotas.")
    return value

def route(data):
    validated = plan(data)
    if not validated["stops"]:
        raise ValueError("Adicione pelo menos uma parada para traçar a rota.")
    lat, lon = number(data.get("lat"), "Latitude", -90, 90), number(data.get("lon"), "Longitude", -180, 180)
    profile = data.get("profile", "foot")
    if not isinstance(profile, str) or profile not in PROFILES:
        raise ValueError("Escolha a pé, carro ou bicicleta.")
    points = [(lon, lat)] + [(p["lon"], p["lat"]) for p in validated["stops"]]
    # Exclui coordenadas arbitrárias fora da região deste protótipo.
    if any(not (-39.20 <= x <= -38.90 and -15.00 <= y <= -14.65) for x,y in points):
        raise ValueError("Escolha um ponto inicial na região de Ilhéus para este protótipo.")
    key = (profile, tuple((round(x, 6), round(y, 6)) for x,y in points))
    with _lock:
        now = time.monotonic()
        cached = _cache.get(key)
        if cached and now-cached[0] < 300:
            raw, cached_hit = cached[1], True
        else:
            global _last_request
            # Política do servidor público: no máximo uma solicitação por segundo.
            delay = 1.05 - (now - _last_request)
            if delay > 0:
                time.sleep(delay)
            _last_request = time.monotonic()
            coordinates = ";".join(f"{x:.6f},{y:.6f}" for x,y in points)
            url = f"https://routing.openstreetmap.de/{PROFILES[profile][0]}/route/v1/driving/{coordinates}?overview=full&geometries=geojson&steps=false"
            raw = _fetch(url)
            if len(_cache) >= 32:
                _cache.pop(next(iter(_cache)))
            if isinstance(raw, dict) and raw.get("code") == "Ok":
                _cache[key] = (time.monotonic(), raw)
            cached_hit = False
    try:
        if raw.get("code") != "Ok" or not raw.get("routes"):
            raise RouteError("Nenhum caminho encontrado pelas ruas para essas paradas. Revise o ponto inicial e as coordenadas.")
        result = raw["routes"][0]
        geometry = result["geometry"]
        coords = geometry["coordinates"]
        if geometry.get("type") != "LineString" or not isinstance(coords, list) or not 2 <= len(coords) <= 80000:
            raise RouteError("Geometria de rota inválida.")
        for coord in coords:
            if not isinstance(coord, list) or len(coord) < 2:
                raise RouteError("Coordenada inválida na rota.")
            for value in coord[:2]:
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                    raise RouteError("Coordenada inválida na rota.")
            if not -180 <= coord[0] <= 180 or not -90 <= coord[1] <= 90:
                raise RouteError("Coordenada fora dos limites.")
        seconds, meters = _metric(result["duration"]), _metric(result["distance"])
        raw_legs = result["legs"]
        if len(raw_legs) != len(validated["stops"]):
            raise RouteError("Quantidade de trechos incompatível com as paradas.")
        names = ["Ponto inicial"] + [p["name"] for p in validated["stops"]]
        legs = [{"from": names[i], "to": names[i+1], "distance_m": round(_metric(leg["distance"])),
                 "duration_minutes": round(_metric(leg["duration"])/60, 1)} for i,leg in enumerate(raw_legs)]
        snaps = raw.get("waypoints", [])
        max_snap = max((_metric(w.get("distance", 0)) for w in snaps), default=0)
        warnings = ["Rota estimada a partir do OpenStreetMap; não inclui trânsito em tempo real.",
                    "Coordenadas dos atrativos são aproximadas. Confirme entradas, acessos e condições locais.",
                    "Nenhuma classificação de segurança ou acessibilidade foi aplicada.",
                    "Gasto de transporte não incluído no orçamento."]
        if max_snap > 100:
            warnings.append(f"Um ponto foi ajustado à rede de caminhos em aproximadamente {round(max_snap)} m. Revise o local antes de usar.")
        travel = round(seconds/60, 1)
        total = round(validated["visit_minutes"] + travel, 1)
        return {"geometry": geometry, "distance_m": round(meters), "travel_minutes": travel,
                "total_minutes": total, "visit_minutes": validated["visit_minutes"],
                "time_exceeded": total > validated["available_minutes"], "profile": profile,
                "profile_label": PROFILES[profile][1], "legs": legs, "warnings": warnings,
                "provider": "FOSSGIS / OSRM · OpenStreetMap", "cached": cached_hit,
                "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    except (KeyError, TypeError, IndexError, AttributeError):
        raise RouteError("Resposta de rota incompleta. Tente novamente.") from None
