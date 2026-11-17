"""Exporta base + adaptador fundido, sem publicação automática."""
import argparse
import json
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
os.environ.setdefault('HF_HOME',str(ROOT.parent/'.model-cache'))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--adapter',default=str(ROOT/'artifacts'/'domain-lora'))
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    from safetensors.torch import load_file
    from ml.lora import attach,load_adapter,merge
    folder=Path(args.adapter);metadata=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    kwargs={'cache_dir':str(ROOT.parent/'.model-cache')}
    if metadata.get('base_revision'):kwargs['revision']=metadata['base_revision']
    tokenizer=AutoTokenizer.from_pretrained(metadata['base_model'],**kwargs)
    model=AutoModelForCausalLM.from_pretrained(metadata['base_model'],torch_dtype=getattr(torch,metadata.get('dtype','float32')),**kwargs)
    attach(model,metadata['rank'],metadata['alpha'],dropout=0)
    load_adapter(model,load_file(str(folder/'adapter.safetensors')))
    model=merge(model)
    destination=Path(args.output);destination.mkdir(parents=True,exist_ok=True)
    model.save_pretrained(destination,safe_serialization=True);tokenizer.save_pretrained(destination)
    card=ROOT/'MODEL_CARD.md'
    if card.exists():(destination/'README.md').write_text(card.read_text(encoding='utf-8'),encoding='utf-8')
    (destination/'training_manifest.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Modelo fundido exportado. Revise os arquivos antes de publicar: '+str(destination.resolve()))

if __name__=='__main__':main()
