"""Entrada ASGI para hospedar os protótipos no Render, sem carregar ML por padrão."""
import json
import mimetypes
import os
import secrets
import threading
import time
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, Response, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from . import server, tourism, brief, routing, chat, llm, local_llm, scheduling
from .config import ROOT

app=FastAPI(title='Protótipos · Amanda Lopes',docs_url=None,redoc_url=None)
secret=os.getenv('SESSION_SECRET')
if not secret:
    raise RuntimeError('Configure SESSION_SECRET com um valor aleatório longo no Render.')
app.add_middleware(SessionMiddleware,secret_key=secret,same_site='lax',https_only=os.getenv('COOKIE_SECURE','true').lower()=='true',max_age=86400)
if os.getenv('APP_DATA_DIR'):
    server.DB_PATH=Path(os.environ['APP_DATA_DIR'])/'briefs.sqlite3'
_limit_lock=threading.Lock()
_requests={}

def session(request):
    if not request.session.get('id'):
        request.session['id']=secrets.token_urlsafe(24)
    return request.session['id']

def owner_record(identifier,sid):
    if isinstance(identifier,bool) or not isinstance(identifier,int):
        raise ValueError('Identificador de versão inválido.')
    with server.db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS web_owners(version_id INTEGER PRIMARY KEY,session_id TEXT NOT NULL)')
        found=conn.execute('SELECT 1 FROM web_owners WHERE version_id=? AND session_id=?',(identifier,sid)).fetchone()
    if not found:
        raise HTTPException(404,'Versão não encontrada nesta sessão.')
    return server.get_record(identifier)

def flags():
    return os.getenv('ENABLE_REMOTE_LLM','false').lower()=='true',os.getenv('ENABLE_TRAINED_LLM','false').lower()=='true'

def permit_models(data):
    remote,trained=flags()
    if data.get('use_llm') is True and not remote:
        raise HTTPException(403,'LLM via API não habilitada neste protótipo hospedado.')
    if data.get('use_trained') is True and not trained:
        raise HTTPException(403,'O modelo treinado funciona no ambiente local. Não está habilitado neste serviço.')

def limit(sid):
    now=time.monotonic()
    with _limit_lock:
        for key in list(_requests):
            _requests[key]=[t for t in _requests[key] if now-t<3600]
            if not _requests[key]:del _requests[key]
        total=sum(len(v) for v in _requests.values())
        if total>=120 or len(_requests.get(sid,[]))>=30:
            raise HTTPException(429,'Limite de demonstração atingido. Tente mais tarde.')
        _requests.setdefault(sid,[]).append(now)

@app.exception_handler(HTTPException)
async def http_error(request,error):
    return JSONResponse({'error':str(error.detail)},status_code=error.status_code)

@app.middleware('http')
async def headers(request,call_next):
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Cache-Control']='no-store'
    return response

@app.get('/api/health')
def health():return {'status':'ok','prototype':True}

@app.get('/api/status')
def status():
    remote,trained=flags()
    return {'llm_configured':remote and llm.configured(),'trained_model_available':trained and local_llm.available(),'recommender':os.getenv('RECOMMENDER','keyword'),'version':'2.1','prototype':True}

@app.get('/api/model')
def model():return local_llm.training_info()

@app.get('/api/evidence')
def evidence():
    file=ROOT/'evidence/batch_benchmark.json'
    return {'batch':json.loads(file.read_text(encoding='utf-8')) if file.exists() else None}

@app.get('/api/briefs')
def history(request:Request):
    sid=session(request)
    with server.db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS web_owners(version_id INTEGER PRIMARY KEY,session_id TEXT NOT NULL)')
        rows=conn.execute('SELECT v.payload FROM versions v JOIN web_owners w ON w.version_id=v.id WHERE w.session_id=? ORDER BY v.id DESC LIMIT 50',(sid,)).fetchall()
    records=[json.loads(r[0]) for r in rows]
    return [{k:r[k] for k in ('id','parent_id','created_at','mode')}|{'title':r['plan']['title']} for r in records]

@app.get('/api/brief')
def get_brief(request:Request,id:int):return owner_record(id,session(request))

@app.get('/api/brief/export')
def export(request:Request,id:int):
    return Response(brief.markdown(owner_record(id,session(request))),media_type='text/markdown')

@app.post('/api/{endpoint:path}')
async def post(endpoint:str,request:Request):
    # Só aceita o mesmo host HTTPS da página; não confia em Origin arbitrário.
    origin=request.headers.get('origin')
    scheme='https' if request.headers.get('x-forwarded-proto')=='https' else request.url.scheme
    if origin and origin!=f"{scheme}://{request.headers.get('host')}":
        raise HTTPException(403,'Origem não permitida.')
    raw=bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw)>64000:raise HTTPException(413,'Entrada maior que 64 KB.')
    try:
        data=json.loads(raw)
        if not isinstance(data,dict):raise ValueError('Envie um objeto JSON.')
    except (ValueError,UnicodeError):
        raise HTTPException(400,'JSON inválido.') from None
    sid=session(request);limit(sid);permit_models(data)
    # Regras e ferramentas síncronas são executadas fora do event loop.
    from starlette.concurrency import run_in_threadpool
    try:return await run_in_threadpool(dispatch,endpoint,data,sid)
    except (llm.ProviderError,routing.RouteError) as error:raise HTTPException(502,str(error)) from None
    except (ValueError,KeyError,TypeError) as error:raise HTTPException(400,str(error)) from None

def dispatch(endpoint,data,sid):
    if endpoint=='tourism/search':return tourism.search(data)
    if endpoint=='tourism/plan':return tourism.plan(data)
    if endpoint=='tourism/route':return routing.route(data)
    if endpoint=='tourism/explain':
        p=tourism.plan(data)
        if not p['stops']:raise ValueError('Selecione uma parada.')
        # O chat oferece a explicação generativa; o botão mantém um resumo verificável.
        return {'mode':'demo','explanation':'Roteiro selecionado: '+ ' → '.join(s['name'] for s in p['stops'])+f". Visitas: {p['visit_minutes']:g} minutos. Gastos simulados; confira a rota para o deslocamento. Para conversar com uma LLM habilitada, use o chat."}
    if endpoint=='chat':
        record=owner_record(data['record_id'],sid) if data.get('record_id') is not None else None
        return chat.answer(data,record)
    if endpoint=='brief/schedule':return scheduling.make(owner_record(data.get('record_id'),sid),data.get('options',{}))
    if endpoint=='briefs/generate':
        if not server.GENERATION_LOCK.acquire(blocking=False):raise HTTPException(409,'Uma geração está em andamento.')
        try:
            parent=data.get('parent_id');previous=None;revision=''
            if parent is None:inputs=brief.validate_input(data)
            else:
                old=owner_record(parent,sid);inputs=old['inputs'];previous=old['plan'];revision=brief.text(data,'revision',3,1500)
            plan,mode=brief.generate(inputs,previous,revision,data.get('use_llm') is True)
            record=server.save_record(inputs,plan,mode,parent,revision)
            with server.db() as conn:
                conn.execute('CREATE TABLE IF NOT EXISTS web_owners(version_id INTEGER PRIMARY KEY,session_id TEXT NOT NULL)')
                conn.execute('INSERT INTO web_owners VALUES(?,?)',(record['id'],sid))
            return record
        finally:server.GENERATION_LOCK.release()
    raise HTTPException(404,'Operação inexistente.')

@app.get('/{path:path}')
def files(path:str):
    aliases={'':'index.html','cacau-trip':'ilheus.html','ilheus':'ilheus.html','buildbrief':'buildbrief.html','como-foi-feito':'how.html','evidencias':'evidence.html'}
    name=aliases.get(path,path)
    allowed={'index.html','ilheus.html','buildbrief.html','how.html','evidence.html','style.css','v2.css','common.js','tourism.js','brief.js','chat.js','planning.js','model.js','evidence.js','amanda.jpg'}
    if name not in allowed:raise HTTPException(404,'Página não encontrada.')
    return FileResponse(ROOT/'web'/name,media_type=mimetypes.guess_type(name)[0])
