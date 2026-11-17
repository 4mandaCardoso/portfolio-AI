"use strict";
async function batchInfo(){const target=$('#batch-info');try{const report=await api('/api/evidence');if(!report.batch){target.textContent='Execute python automation/run_batch.py para registrar uma medição.';return;}
  const b=report.batch,metrics=el('div',null,'metrics');[[b.files_generated,'Planos exportados'],[b.total_seconds.toFixed(4)+' s','Tempo automático local'],['Não medido','Tempo humano economizado']].forEach(([v,k])=>{const card=el('div',null,'metric');card.append(el('strong',v),el('span',k));metrics.append(card);});target.append(metrics);
  const list=el('ul',null,'clean muted');b.cases.forEach(r=>list.append(el('li',`${r.idea} · ${r.validated?'formato validado':'não validado'}`)));target.append(list,el('p',b.scope,'tiny muted'));
}catch(error){target.textContent=error.message;}}batchInfo();
