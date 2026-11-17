"""Inferência opcional do adaptador realmente treinado; importação pesada sob demanda."""
import importlib.util
import json
import os
import threading
from functools import lru_cache
from .config import ROOT
from .llm import ProviderError

FOLDER=ROOT/'ml'/'artifacts'/'domain-lora'
LOCK=threading.Lock()

def training_info():
    try:
        os.environ.setdefault('HF_HOME',str(ROOT/'.model-cache'))
        os.environ.setdefault('TORCH_HOME',str(ROOT/'.model-cache'/'torch'))
        data=json.loads((FOLDER/'manifest.json').read_text(encoding='utf-8'))
        if data.get('status')=='trained' and (FOLDER/'adapter.safetensors').is_file():
            return data
    except (OSError,ValueError,TypeError):
        pass
    return {'status':'not_trained'}

def available():
    return training_info()['status']=='trained' and all(importlib.util.find_spec(name) is not None for name in ('torch','transformers','safetensors','psutil'))

@lru_cache(maxsize=1)
def load():
    if not available():
        raise ProviderError('O adaptador treinado ou as dependências não estão disponíveis. Use INICIAR_IA_TREINADA.bat e consulte ml/README.md.')
    try:
        import torch
        from transformers import AutoModelForCausalLM,AutoTokenizer
        from safetensors.torch import load_file
        from ml.lora import attach,load_adapter
        import psutil
        if psutil.virtual_memory().available<900_000_000:
            raise ProviderError('Pouca memória livre para a LLM local. Feche aplicativos ou use o modo por regras/API.')
        torch.set_num_threads(4)
        manifest=training_info()
        kwargs={'cache_dir':str(ROOT/'.model-cache')}
        if manifest.get('base_revision'):kwargs['revision']=manifest['base_revision']
        tokenizer=AutoTokenizer.from_pretrained(manifest['base_model'],**kwargs)
        if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
        tokenizer.truncation_side='left'
        model=AutoModelForCausalLM.from_pretrained(manifest['base_model'],torch_dtype=getattr(torch,manifest.get('dtype','float32')),attn_implementation='sdpa',**kwargs)
        attach(model,rank=manifest['rank'],alpha=manifest['alpha'],dropout=0)
        load_adapter(model,load_file(str(FOLDER/'adapter.safetensors')))
        model.eval()
        return tokenizer,model
    except ProviderError:
        raise
    except Exception:
        raise ProviderError('Não foi possível carregar a LLM ajustada. Confira dependências, internet no primeiro download e os arquivos do adaptador.') from None

def reply(project,message,history,context):
    if not LOCK.acquire(blocking=False):
        raise ProviderError('A LLM local já está respondendo. Aguarde e tente novamente.')
    try:
        import torch
        tokenizer,model=load()
        from ml.build_dataset import SYSTEM
        # Limita o contexto para o modelo compacto; as ferramentas mantêm a fonte de verdade.
        summary=json.dumps(context,ensure_ascii=False)[:1700]
        messages=[{'role':'system','content':SYSTEM+' Você não modifica o projeto. Responda de forma breve; o modelo é experimental.'}]
        for item in history[-2:]:messages.append({'role':item['role'],'content':item['content'][:500]})
        messages.append({'role':'user','content':f'Projeto: {project}. Contexto: {summary}\nPergunta: {message}'})
        prompt=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        inputs=tokenizer(prompt,return_tensors='pt',truncation=True,max_length=768)
        with torch.no_grad():
            output=model.generate(**inputs,max_new_tokens=140,do_sample=False,repetition_penalty=1.1,no_repeat_ngram_size=4,pad_token_id=tokenizer.pad_token_id,use_cache=True)
        result=tokenizer.decode(output[0,inputs['input_ids'].shape[-1]:],skip_special_tokens=True).strip()
        if not result:raise ProviderError('A LLM ajustada retornou uma resposta vazia. Tente uma pergunta mais curta.')
        return result[:4000]
    except ProviderError:
        raise
    except Exception:
        raise ProviderError('Falha na inferência da LLM local. Consulte ml/README.md; não houve alteração automática no projeto.') from None
    finally:
        LOCK.release()
