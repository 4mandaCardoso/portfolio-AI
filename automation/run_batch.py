"""Automatiza planos, cronogramas e exportações; mede duração, não inventa horas poupadas."""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from backend import brief,scheduling

IDEAS=['Um sistema de reservas para uma pousada','Um sistema de estoque de produtos','Um planejador de roteiros de turismo','Uma ferramenta de tarefas pessoais','Um sistema de chamados de atendimento']

def main():
    dest=ROOT/'runtime'/'batch-exports';dest.mkdir(parents=True,exist_ok=True)
    rows=[];started=time.perf_counter()
    for index,idea in enumerate(IDEAS,1):
        began=time.perf_counter()
        inputs=brief.validate_input({'idea':idea,'audience':'Equipe pequena','deadline':'1 semana','technologies':'Python e JavaScript','constraints':'Sem pagamentos online'})
        plan,mode=brief.generate(inputs)
        record={'id':index,'plan':plan,'inputs':inputs,'mode':mode,'created_at':datetime.now(timezone.utc).isoformat()}
        schedule=scheduling.make(record)
        content=brief.markdown(record)+'\n\n## Cronograma\n'+json.dumps(schedule,ensure_ascii=False,indent=2)
        filename=f'plano-{index:02d}.md';(dest/filename).write_text(content,encoding='utf-8')
        rows.append({'idea':idea,'output':filename,'seconds':round(time.perf_counter()-began,6),'validated':True})
    report={'run_at':datetime.now(timezone.utc).isoformat(),'mode':'deterministic_local_template','cases':rows,
            'total_seconds':round(time.perf_counter()-started,6),'files_generated':len(rows),
            'manual_baseline_seconds':None,'real_hours_saved':None,
            'scope':'Execução local de cinco exemplos sintéticos. Não mede tempo de trabalho humano nem uso por terceiros.'}
    target=ROOT/'evidence';target.mkdir(exist_ok=True)
    (target/'batch_benchmark.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'files':len(rows),'seconds':report['total_seconds'],'report':str(target/'batch_benchmark.json')}))

if __name__=='__main__':main()
