"""SFT real com LoRA e avaliação antes/depois. Não envia pesos para contas externas."""
import argparse
import hashlib
import json
import math
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
os.environ.setdefault('HF_HOME',str(ROOT.parent/'.model-cache'))
os.environ.setdefault('TORCH_HOME',str(ROOT.parent/'.model-cache'/'torch'))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--model',default='Qwen/Qwen2.5-0.5B-Instruct')
    parser.add_argument('--max-steps',type=int,default=24,help='Atualizações de otimizador, não exemplos individuais')
    parser.add_argument('--epochs',type=int,default=2)
    parser.add_argument('--rank',type=int,default=8)
    parser.add_argument('--learning-rate',type=float,default=0.0002)
    parser.add_argument('--max-length',type=int,default=192)
    parser.add_argument('--threads',type=int,default=4)
    parser.add_argument('--dtype',choices=['float32','bfloat16'],default='float32')
    parser.add_argument('--output',default=str(ROOT/'artifacts'/'domain-lora'))
    args=parser.parse_args()
    if args.max_steps<1 or args.epochs<1 or not 64<=args.max_length<=1024:
        parser.error('Parâmetros de treinamento inválidos.')
    import torch
    import transformers
    import psutil
    from safetensors.torch import save_file
    from transformers import AutoModelForCausalLM,AutoTokenizer
    from ml.lora import attach,adapter_state
    random.seed(42);torch.manual_seed(42);torch.set_num_threads(args.threads)
    if psutil.virtual_memory().available<1_000_000_000:
        raise SystemExit('Menos de 1 GB livre. Feche aplicativos ou execute em um ambiente com mais memória.')
    from ml.build_dataset import main as build
    if not (ROOT/'data'/'train.jsonl').exists():build()
    raw_train=[json.loads(line) for line in (ROOT/'data'/'train.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    raw_eval=[json.loads(line) for line in (ROOT/'data'/'eval.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    if {r['messages'][-2]['content'] for r in raw_train}&{r['messages'][-2]['content'] for r in raw_eval}:
        raise ValueError('Perguntas de avaliação encontradas no treinamento.')
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    print('Carregando modelo e tokenizer públicos; o primeiro uso exige download.',flush=True)
    tokenizer=AutoTokenizer.from_pretrained(args.model,cache_dir=str(ROOT.parent/'.model-cache'))
    if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
    model=AutoModelForCausalLM.from_pretrained(args.model,torch_dtype=getattr(torch,args.dtype),attn_implementation='sdpa',cache_dir=str(ROOT.parent/'.model-cache'))
    model.config.use_cache=False
    replaced=attach(model,rank=args.rank,alpha=args.rank*2)
    trainable=sum(p.numel() for p in model.parameters() if p.requires_grad)
    total=sum(p.numel() for p in model.parameters())
    print(f'Parâmetros treináveis: {trainable:,} / {total:,}; {len(replaced)} projeções adaptadas.',flush=True)
    def encode(row):
        messages=row['messages']
        prompt=tokenizer.apply_chat_template(messages[:-1],tokenize=False,add_generation_prompt=True)
        full=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=False)
        p=tokenizer(prompt,add_special_tokens=False)['input_ids']
        f=tokenizer(full,add_special_tokens=False)['input_ids']
        response=f[len(p):]
        # Mantém a resposta supervisionada e limita o contexto com transparência.
        max_prompt=args.max_length//2
        if len(p)>max_prompt:p=p[-max_prompt:]
        response=response[:args.max_length-len(p)]
        if not response:raise ValueError('Exemplo sem tokens de resposta.')
        ids=torch.tensor([p+response],dtype=torch.long)
        labels=ids.clone();labels[:,:len(p)]=-100
        return {'input_ids':ids,'attention_mask':torch.ones_like(ids),'labels':labels}
    train=[encode(r) for r in raw_train];evaluation=[encode(r) for r in raw_eval]
    def evaluate():
        model.eval();weighted=0;tokens=0
        with torch.no_grad():
            for sample in evaluation:
                loss=model(**sample).loss.item();count=(sample['labels'][:,1:]!=-100).sum().item()
                weighted+=loss*count;tokens+=count
        return weighted/max(tokens,1)
    def answers():
        model.eval();rows=[]
        for raw in raw_eval[:2]:
            prompt=tokenizer.apply_chat_template(raw['messages'][:-1],tokenize=False,add_generation_prompt=True)
            inputs=tokenizer(prompt,return_tensors='pt',truncation=True,max_length=512)
            with torch.no_grad():pred=model.generate(**inputs,max_new_tokens=90,do_sample=False,pad_token_id=tokenizer.pad_token_id,use_cache=True)
            response=tokenizer.decode(pred[0,inputs['input_ids'].shape[-1]:],skip_special_tokens=True)
            rows.append({'id':raw['id'],'question':raw['messages'][-2]['content'],'response':response,'reference':raw['messages'][-1]['content']})
        return rows
    (output/'training_log.jsonl').write_text('',encoding='utf-8')
    began=time.perf_counter();before=evaluate();baseline=answers()
    print(f'Loss de avaliação antes: {before:.4f}',flush=True)
    optimizer=torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),lr=args.learning_rate)
    logs=[];steps=0;accumulation=2;stop=False
    for epoch in range(args.epochs):
        order=list(range(len(train)));random.shuffle(order);model.train();optimizer.zero_grad(set_to_none=True);pending=0;running=0.0
        for pos,index in enumerate(order):
            sample=train[index];loss=model(**sample).loss
            if not torch.isfinite(loss):raise RuntimeError('Loss não finita. Treinamento interrompido sem publicar pesos.')
            (loss/accumulation).backward();pending+=1;running+=loss.item()
            if pending==accumulation or pos==len(order)-1:
                torch.nn.utils.clip_grad_norm_((p for p in model.parameters() if p.requires_grad),1.0)
                optimizer.step();optimizer.zero_grad(set_to_none=True);steps+=1
                entry={'step':steps,'epoch':epoch+1,'train_loss':running/pending,'elapsed_seconds':round(time.perf_counter()-began,2)}
                logs.append(entry)
                with (output/'training_log.jsonl').open('a',encoding='utf-8') as handle:handle.write(json.dumps(entry)+'\n')
                print(json.dumps(entry),flush=True);pending=0;running=0.0
                if steps>=args.max_steps:stop=True;break
        if stop:break
    after=evaluate();adapted=answers()
    weights=adapter_state(model)
    save_file(weights,str(output/'adapter.safetensors'))
    if not any(torch.count_nonzero(value).item() for key,value in weights.items() if key.endswith('lora_B')):
        raise RuntimeError('O adaptador não contém atualização efetiva.')
    revision=getattr(model.config,'_commit_hash',None)
    ref=ROOT.parent/'.model-cache'/('models--'+args.model.replace('/','--'))/'refs'/'main'
    if revision is None and ref.exists():revision=ref.read_text(encoding='utf-8').strip()
    manifest={'status':'trained','base_model':args.model,'base_revision':revision,'method':'Supervised fine-tuning with native LoRA on q_proj/v_proj',
              'rank':args.rank,'alpha':args.rank*2,'targets':['q_proj','v_proj'],'trainable_parameters':trainable,'total_parameters_with_adapter':total,
              'optimizer_steps':steps,'learning_rate':args.learning_rate,'gradient_accumulation':accumulation,'seed':42,'max_length':args.max_length,
              'train_examples':len(train),'eval_examples':len(evaluation),'eval_loss_before':before,'eval_loss_after':after,
              'elapsed_seconds':round(time.perf_counter()-began,2),'device':'cpu','threads':args.threads,
              'torch_version':torch.__version__,'transformers_version':transformers.__version__,'dtype':args.dtype,
              'trained_at':datetime.now(timezone.utc).isoformat(),'dataset_origin':'Synthetic author-created Portuguese examples; no private user chats.',
              'train_sha256':hashlib.sha256((ROOT/'data'/'train.jsonl').read_bytes()).hexdigest(),
              'eval_sha256':hashlib.sha256((ROOT/'data'/'eval.jsonl').read_bytes()).hexdigest(),
              'limitations':['Small multilingual base; Portuguese domain adaptation is limited.' if args.model.startswith('Qwen/') else 'Base model is primarily English; Portuguese quality is limited.','Small synthetic evaluation with related topics; not an independent quality benchmark.','Lower teacher-forced loss is not proof of factual correctness or better user experience.']}
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (output/'comparison.json').write_text(json.dumps({'before':baseline,'after':adapted},ensure_ascii=False,indent=2),encoding='utf-8')
    print('TREINAMENTO CONCLUÍDO: '+str(output),flush=True)
    print(json.dumps({'before':before,'after':after,'steps':steps,'seconds':manifest['elapsed_seconds']}),flush=True)

if __name__=='__main__':main()
