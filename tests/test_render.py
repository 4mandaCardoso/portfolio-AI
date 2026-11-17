import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))

@unittest.skipUnless(importlib.util.find_spec('fastapi') is not None and importlib.util.find_spec('httpx') is not None,'Teste opcional: requer ambiente Render/FastAPI e httpx.')
class RenderTests(unittest.TestCase):
    def test_health_origin_history_isolation_and_export(self):
        os.environ.setdefault('SESSION_SECRET','test-only-session-secret-not-for-deployment')
        from backend import server,webapp
        from fastapi.testclient import TestClient
        data={'idea':'Sistema de reservas para pousadas','audience':'Equipe','deadline':'1 semana','technologies':'Python','constraints':'Sem pagamentos'}
        with tempfile.TemporaryDirectory() as tmp,patch.object(server,'DB_PATH',Path(tmp)/'test.sqlite3'):
            a=TestClient(webapp.app,base_url='https://testserver')
            b=TestClient(webapp.app,base_url='https://testserver')
            self.assertEqual(a.get('/api/health').status_code,200)
            self.assertEqual(a.get('/').status_code,200)
            r=a.post('/api/briefs/generate',json=data)
            self.assertEqual(r.status_code,200,r.text)
            record=r.json();identifier=record['id']
            self.assertEqual(len(a.get('/api/briefs').json()),1)
            self.assertEqual(b.get('/api/briefs').json(),[])
            self.assertEqual(b.get('/api/brief',params={'id':identifier}).status_code,404)
            self.assertEqual(a.get('/api/brief/export',params={'id':identifier}).status_code,200)
            self.assertEqual(a.post('/api/tourism/plan',json={},headers={'Origin':'https://other.example'}).status_code,403)
            self.assertEqual(a.get('/.env').status_code,404)
            self.assertEqual(a.post('/api/chat',json={'project':'brief','message':'Oi','use_trained':True}).status_code,403)

if __name__=='__main__':unittest.main()
