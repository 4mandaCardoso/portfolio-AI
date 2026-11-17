import copy
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.request
import urllib.error
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend import tourism, brief, server, llm

INPUT = {"idea": "Um sistema de reservas para pousadas", "audience": "Recepcionistas", "deadline": "1 semana", "technologies": "Python", "constraints": "Sem pagamentos"}

class TourismTests(unittest.TestCase):
    def test_distance(self):
        self.assertEqual(tourism.distance(0, 0, 0, 0), 0)
        self.assertAlmostEqual(tourism.distance(0, 0, 0, 1), 111.195, places=2)

    def test_retrieval_and_empty(self):
        with patch.dict(os.environ, {"RECOMMENDER": "keyword"}):
            found = tourism.search({"lat": -14.8004, "lon": -39.0331, "interests": "literatura museu", "radius": 3})
            self.assertEqual(found["places"][0]["id"], "jorge-amado")
            self.assertEqual(tourism.search({"lat": 0, "lon": 0})["places"], [])

    def test_cost_group_time_and_budget(self):
        p = tourism.plan({"stops": [{"id": "catedral", "duration": 60, "cost_min": 10, "cost_max": 20}, {"id": "vesuvio", "duration": 90, "cost_min": 40, "cost_max": 70}], "group": 3, "budget": 80, "minutes": 100})
        self.assertEqual(p["cost_person"], [50, 90])
        self.assertEqual(p["cost_group"], [150, 270])
        self.assertEqual(p["visit_minutes"], 150)
        self.assertTrue(p["time_exceeded"])
        self.assertTrue(p["budget_exceeded"])
        self.assertFalse(p["transport_included"])

    def test_invalid_inputs(self):
        for data in [{"group": 1.5}, {"group": True}, {"minutes": "nan"}, {"budget": -1}, {"budget": "inf"}, {"stops": [{"id": "unknown"}]}, {"stops": [{"id": "catedral", "cost_min": 10, "cost_max": 5}]}, {"stops": [{"id": "catedral"}, {"id": "catedral"}]}]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                tourism.plan(data)

class BriefTests(unittest.TestCase):
    def test_valid_template_and_revision(self):
        initial, mode = brief.generate(INPUT)
        self.assertEqual(mode, "demo")
        snapshot = copy.deepcopy(initial)
        revised, _ = brief.generate(INPUT, initial, "retire pagamentos online")
        self.assertEqual(initial, snapshot)
        self.assertIn("Pagamentos online excluídos conforme revisão.", revised["out_of_scope"])
        other, _ = brief.generate(INPUT, revised, "adicione notificacoes")
        self.assertIn("Pagamentos online excluídos conforme revisão.", other["out_of_scope"])
        self.assertTrue(any("pendente" in q for q in other["questions"]))

    def test_broken_references_and_empty_criteria(self):
        p = brief.demo(INPUT)
        p["tasks"][0]["requirement_id"] = "RF999"
        with self.assertRaises(ValueError): brief.validate_plan(p)
        p = brief.demo(INPUT)
        p["stories"][0]["acceptance"] = []
        with self.assertRaises(ValueError): brief.validate_plan(p)
        p = brief.demo(INPUT)
        p["requirements"][1]["id"] = "RF01"
        with self.assertRaises(ValueError): brief.validate_plan(p)

    def test_llm_validation_without_network(self):
        invalid = brief.demo(INPUT)
        invalid["tasks"][0]["requirement_id"] = "inexistente"
        with patch.object(llm, "json_complete", return_value=invalid):
            with self.assertRaises(llm.ProviderError): brief.generate(INPUT, use_llm=True)
        with patch.object(llm, "json_complete", return_value=brief.demo(INPUT)):
            self.assertEqual(brief.generate(INPUT, use_llm=True)[1], "llm")

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db_patch = patch.object(server, "DB_PATH", Path(cls.tmp.name) / "test.sqlite3")
        cls.db_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls.db_patch.stop(); cls.tmp.cleanup()

    def request(self, path, data=None, headers=None):
        # Executa o parser HTTP e os handlers reais em memoria: sem permissao de rede.
        payload = b"" if data is None else json.dumps(data).encode()
        method = "GET" if data is None else "POST"
        fields = {"Host": "127.0.0.1:8000", "Content-Length": str(len(payload)), **(headers or {})}
        raw = (method + " " + path + " HTTP/1.1\r\n" + "\r\n".join(k+": "+v for k,v in fields.items()) + "\r\n\r\n").encode() + payload
        class Socket:
            def __init__(self): self.output = io.BytesIO()
            def makefile(self, *_): return io.BytesIO(raw)
            def sendall(self, value): self.output.write(value)
        class QuietHandler(server.Handler):
            def log_message(self, *_): pass
        sock = Socket()
        QuietHandler(sock, ("127.0.0.1", 12345), SimpleNamespace(server_port=8000))
        head, body = sock.output.getvalue().split(b"\r\n\r\n", 1)
        status = int(head.split(b" ")[1])
        if status >= 400:
            raise urllib.error.HTTPError(path, status, "HTTP error", {}, io.BytesIO(body))
        return body, status

    def test_pages_and_private_files(self):
        for path in ("/", "/ilheus", "/buildbrief", "/style.css", "/tourism.js"):
            self.assertEqual(self.request(path)[1], 200)
        for path in ("/.env", "/data/places.json", "/../backend/config.py"):
            with self.assertRaises(urllib.error.HTTPError) as context: self.request(path)
            self.assertEqual(context.exception.code, 404)
            context.exception.close()

    def test_complete_versioned_workflow(self):
        record = json.loads(self.request("/api/briefs/generate", INPUT)[0])
        child = json.loads(self.request("/api/briefs/generate", {"parent_id": record["id"], "revision": "retire pagamentos"})[0])
        self.assertEqual(child["parent_id"], record["id"])
        restored = json.loads(self.request("/api/brief?id=" + str(record["id"]))[0])
        self.assertEqual(restored, record)
        self.assertIn(b"Requisitos", self.request("/api/brief/export?id=" + str(child["id"]))[0])

    def test_explanation_no_network(self):
        p = {"stops": [{"id": "catedral"}]}
        result = json.loads(self.request("/api/tourism/explain", p)[0])
        self.assertEqual(result["mode"], "demo")
        self.assertIn("Catedral", result["explanation"])

    def test_cross_origin_and_bad_input(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.request("/api/briefs/generate", INPUT, {"Origin": "https://example.org"})
        self.assertEqual(ctx.exception.code, 403)
        ctx.exception.close()
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.request("/api/tourism/plan", {"group": -1})
        self.assertEqual(ctx.exception.code, 400)
        ctx.exception.close()

if __name__ == "__main__": unittest.main()
