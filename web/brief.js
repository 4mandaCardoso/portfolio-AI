"use strict";
let current=null,busy=false;
const inputNames=['idea','audience','deadline','technologies','constraints'];
function setBusy(value){busy=value;$('#generate').disabled=value;$('#revise').disabled=value;$('#refresh-history').disabled=value;document.querySelectorAll('.history-item').forEach(b=>b.disabled=value);}
function section(title){const node=el('section',null,'plan-section');node.append(el('h3',title));return node;}
function listSection(title,items){const node=section(title),ul=el('ul',null,'clean muted');items.forEach(item=>ul.append(el('li',item)));node.append(ul);return node;}
function render(record){
  current=record;const p=record.plan;$('#empty').classList.add('hidden');$('#plan').classList.remove('hidden');$('#revision-panel').classList.remove('hidden');
  const root=$('#plan');root.replaceChildren();const top=el('div',null,'row between');
  top.append(el('span',`VERSÃO ${record.id}${record.parent_id?' · derivada de '+record.parent_id:''}`,'eyebrow'));
  const exportButton=el('button','Baixar Markdown ↓','secondary small');exportButton.onclick=async()=>{try{const r=await fetch('/api/brief/export?id='+record.id);if(!r.ok)throw new Error('Não foi possível exportar.');download(`buildbrief-v${record.id}.md`,(await r.text()) + planningMarkdown());}catch(error){message(error.message,true);}};top.append(exportButton);
  root.append(top,el('h2',p.title),el('p',p.objective,'muted'),el('span',record.mode==='llm'?'LLM conectada · conteúdo requer revisão':'Demonstração por template · sem LLM','pill'),el('p',`Público: ${p.audience}`,'tiny muted'));
  root.append(el('p',p.revision_summary,'notice info'));
  const context=section('Contexto informado');context.append(el('p',`Prazo: ${record.inputs.deadline} · Tecnologias: ${record.inputs.technologies}`,'tiny muted'),el('p',`Restrições: ${record.inputs.constraints||'Não informadas'}`,'tiny muted'));root.append(context);
  root.append(listSection('Suposições a confirmar',p.assumptions),listSection('Perguntas em aberto',p.questions));
  const req=section('Requisitos funcionais');p.requirements.forEach(item=>{const node=el('div',null,'plan-item');node.append(el('span',item.id,'pill'),el('p',item.description));req.append(node);});root.append(req);
  const stories=section('Histórias & critérios de aceitação');p.stories.forEach(item=>{const node=el('div',null,'plan-item');node.append(el('span',`${item.id} → ${item.requirement_id}`,'pill'),el('p',item.description));const ul=el('ul');item.acceptance.forEach(a=>ul.append(el('li',a)));node.append(ul);stories.append(node);});root.append(stories);
  const entities=section('Modelo inicial de dados');p.entities.forEach(item=>{const node=el('div',null,'plan-item wrap');node.append(el('strong',item.name),el('p',item.fields.join(' · '),'tiny muted'));entities.append(node);});root.append(entities);
  const tasks=section('Tarefas rastreáveis');p.tasks.forEach(item=>{const node=el('div',null,'plan-item');node.append(el('span',`${item.id} → ${item.requirement_id}`,'pill'),el('p',item.title),el('p','Concluída quando: '+item.done_when,'tiny muted'));tasks.append(node);});root.append(tasks);
  root.append(listSection('Fora do escopo',p.out_of_scope),listSection('Riscos & limitações',p.risks));
  if(record.revision)root.append(el('p','Pedido de revisão: '+record.revision,'notice'));
  root.append(el('p',`Salvo em ${new Date(record.created_at).toLocaleString('pt-BR')}. Validação de formato e referências não garante correção técnica.`,'tiny muted'));
  inputNames.forEach(name=>$('#'+name).value=record.inputs[name]);
  loadSchedule(record.id);
}
async function history(){
  try{const records=await api('/api/briefs'),root=$('#history');root.replaceChildren();
    if(!records.length)root.append(el('p','Nenhuma versão salva ainda.','tiny muted'));
    records.forEach(record=>{const button=el('button',`v${record.id} · ${record.title} ${record.parent_id?'↳ v'+record.parent_id:''}`,'history-item');button.disabled=busy;
      button.onclick=async()=>{if(busy)return;try{render(await api('/api/brief?id='+record.id));message(`Versão ${record.id} carregada.`);}catch(error){message(error.message,true);}};root.append(button);});
  }catch(error){message(error.message,true);}
}
$('#brief-form').onsubmit=async event=>{
  event.preventDefault();if(busy)return;setBusy(true);message($('#use-llm').checked?'Consultando a LLM…':'Preparando plano demonstrativo…');
  try{const payload=Object.fromEntries(inputNames.map(name=>[name,$('#'+name).value]));payload.use_llm=$('#use-llm').checked;
    render(await api('/api/briefs/generate',payload));message('Plano salvo. Revise as suposições e os critérios.');await history();
  }catch(error){message(error.message,true);}finally{setBusy(false);}
};
$('#revision-form').onsubmit=async event=>{
  event.preventDefault();if(!current||busy)return;setBusy(true);message('Gerando nova versão…');
  try{const payload={parent_id:current.id,revision:$('#revision').value,use_llm:$('#use-llm').checked};render(await api('/api/briefs/generate',payload));$('#revision').value='';message('Nova versão salva. A anterior continua disponível.');await history();
  }catch(error){message(error.message,true);}finally{setBusy(false);}
};
$('#refresh-history').onclick=()=>history();setupMode();history();

initPlanning();
const briefChat=initChat({project:'brief',title:'Assistente BuildBrief',
  welcome:'Olá! Conte sua ideia ou gere um plano. Posso explicar requisitos, critérios, tarefas, estimativas de prazo e preparar revisões.',
  prompts:['Por onde começar?','Explique os critérios de aceitação','Quais são os possíveis prazos?'],
  context:()=>({record_id:current?.id??null,context:{form:Object.fromEntries(inputNames.map(n=>[n,$('#'+n).value])),schedule_options:scheduleOptions()}}),
  revise:action=>{if(!current||current.id!==action.parent_id){message('Carregue a versão mencionada antes de revisar.',true);return;}$('#revision').value=action.text;$('#revision-panel').scrollIntoView({behavior:'smooth',block:'center'});$('#revision').focus();}
});
