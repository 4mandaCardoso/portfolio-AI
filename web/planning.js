"use strict";
let scheduleRecord=null,scheduleResult=null,scheduleVersion=0;
const svgNS='http://www.w3.org/2000/svg';
function svgNode(name,attrs,text){const node=document.createElementNS(svgNS,name);Object.entries(attrs||{}).forEach(([key,value])=>node.setAttribute(key,String(value)));if(text!==undefined)node.textContent=text;return node;}
function drawFlowchart(schedule){
  const rows=schedule.rows,height=rows.length*112+310;
  const svg=svgNode('svg',{viewBox:`0 0 760 ${height}`,role:'img','aria-label':'Fluxograma de fases, tarefas, validação e entrega'});
  svg.append(svgNode('title',{},'Fluxograma do planejamento'),svgNode('desc',{},'Sequência proposta para uma pessoa: descoberta, tarefas, testes, validação e entrega. Se os critérios não forem atendidos, voltar aos ajustes e testes.'));
  const defs=svgNode('defs'),marker=svgNode('marker',{id:'flow-arrow',viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:7,markerHeight:7,orient:'auto-start-reverse'});marker.append(svgNode('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'#b67a4c'}));defs.append(marker);svg.append(defs);
  function arrow(d){svg.append(svgNode('path',{d,stroke:'#b67a4c','stroke-width':2,fill:'none','marker-end':'url(#flow-arrow)'}));}
  function label(text,x,y,size=14,fill='#43271c'){svg.append(svgNode('text',{x,y,'text-anchor':'middle','font-size':size,fill},text));}
  const short=(text,n)=>text.length>n?text.slice(0,n-1)+'…':text;
  rows.forEach((row,i)=>{
    const y=25+i*112;
    if(i)arrow(`M 350 ${y-29} L 350 ${y}`);
    const group=svgNode('g');group.append(svgNode('rect',{x:115,y,width:470,height:82,rx:16,fill:row.kind==='task'?'#fff':'#fff0d9',stroke:'#d9b58f','stroke-width':1.5}),svgNode('title',{},row.title));svg.append(group);
    label((row.task_id||row.id)+' · '+short(row.title,47),350,y+29,14);
    label(`${row.min_hours}–${row.max_hours} h · ${formatDate(row.start_early)} → ${formatDate(row.finish_late)}`,350,y+55,12,'#826e62');
  });
  const y=25+rows.length*112;arrow(`M 350 ${y-30} L 350 ${y}`);
  svg.append(svgNode('polygon',{points:`350,${y} 500,${y+65} 350,${y+130} 200,${y+65}`,fill:'#fff1d9',stroke:'#e08a3d','stroke-width':1.5}));label('Critérios atendidos?',350,y+68,15);
  arrow(`M 350 ${y+130} L 350 ${y+175}`);label('Sim',375,y+153,12);
  svg.append(svgNode('rect',{x:180,y:y+178,width:340,height:62,rx:18,fill:'#155b43'}));label('Entrega validada',350,y+215,17,'#fff');
  const qaIndex=rows.findIndex(r=>r.id==='QA'),returnY=25+qaIndex*112+41;
  arrow(`M 500 ${y+65} L 665 ${y+65} L 665 ${returnY} L 586 ${returnY}`);label('Não: ajustar',588,y+49,12);
  $('#flowchart').replaceChildren(svg);
}
function formatDate(iso){const parts=iso.split('-');return `${parts[2]}/${parts[1]}/${parts[0]}`;}
function scheduleOptions(){
  return {start_date:$('#schedule-start').value,hours_day:$('#schedule-hours').value,complexity:$('#schedule-complexity').value,
    overrides:Array.from(document.querySelectorAll('[data-estimate-id]')).map(row=>({id:row.dataset.estimateId,min_hours:row.querySelector('[data-min]').value,max_hours:row.querySelector('[data-max]').value}))};
}
async function loadSchedule(recordId,reset=true){
  const oldRecord=scheduleRecord;scheduleRecord=recordId;const version=++scheduleVersion;
  $('#schedule-panel').classList.remove('hidden');$('#schedule-status').textContent='Calculando estimativas…';
  if(reset||oldRecord!==recordId){$('#schedule-rows').replaceChildren();scheduleResult=null;}
  const options=scheduleOptions();
  try{const result=await api('/api/brief/schedule',{record_id:recordId,options});if(version!==scheduleVersion)return;scheduleResult=result;renderSchedule(result);$('#schedule-status').textContent='Estimativas atualizadas. Revise a capacidade e o esforço por tarefa.';}
  catch(error){if(version===scheduleVersion){$('#schedule-status').textContent=error.message;scheduleResult=null;$('#flowchart').replaceChildren();}}
}
function renderSchedule(result){
  $('#schedule-start').value=result.start_date;
  const root=$('#schedule-rows');root.replaceChildren();
  result.rows.forEach(row=>{
    const tr=el('tr'),name=el('td');name.append(el('strong',row.task_id||row.id),el('div',row.title),el('small',row.depends_on?'Depende de '+row.depends_on:'Início do planejamento','muted'));tr.append(name);
    ['min_hours','max_hours'].forEach((key,index)=>{const td=el('td');if(row.kind==='task'){tr.dataset.estimateId=row.task_id;const input=el('input');input.type='number';input.min='.5';input.max='1000';input.step='.5';input.value=row[key];input.setAttribute(index?'data-max':'data-min','');input.setAttribute('aria-label',(index?'Horas máximas de ':'Horas mínimas de ')+row.title);td.append(input);}else td.textContent=row[key];tr.append(td);});
    tr.append(el('td',formatDate(row.start_early)+' → '+formatDate(row.finish_late)));root.append(tr);
  });
  $('#schedule-summary').textContent=`Esforço total: ${result.min_hours}–${result.max_hours} h · ${result.min_workdays}–${result.max_workdays} dias úteis · conclusão estimada entre ${formatDate(result.finish_early)} e ${formatDate(result.finish_late)}.`;
  const assumptions=$('#schedule-assumptions');assumptions.replaceChildren();result.assumptions.forEach(a=>assumptions.append(el('li',a)));drawFlowchart(result);
}
function planningMarkdown(){
  if(!scheduleResult)return '';
  const s=scheduleResult,lines=['','## Cronograma estimado',`Capacidade: ${s.hours_day} h/dia. Complexidade: ${s.complexity}.`,
    `Esforço: ${s.min_hours}–${s.max_hours} h. Conclusão: ${s.finish_early} a ${s.finish_late}.`,'', '| Fase/tarefa | Horas | Dependência | Início mais cedo | Fim mais tarde |','| --- | --- | --- | --- | --- |'];
  s.rows.forEach(r=>lines.push(`| ${r.id}: ${r.title.replaceAll('|','/')} | ${r.min_hours}–${r.max_hours} | ${r.depends_on||'—'} | ${r.start_early} | ${r.finish_late} |`));
  lines.push('','### Suposições',...s.assumptions.map(a=>'- '+a),'','### Fluxograma (Mermaid)','```mermaid','flowchart TD');
  s.rows.forEach((r,i)=>{const label=(r.task_id||r.id)+' '+r.title;lines.push(`N${i}["${label.replace(/["<>\[\]{}]/g,'').replaceAll('\n',' ')}"]`);if(i)lines.push(`N${i-1} --> N${i}`);});
  lines.push(`N${s.rows.length-1} --> CHECK{"Critérios atendidos?"}`,'CHECK -->|Sim| END["Entrega validada"]',`CHECK -->|Não| N${s.rows.findIndex(r=>r.id==='QA')}`,'```');return lines.join('\n');
}
function initPlanning(){
  const dateParts=new Intl.DateTimeFormat('en-CA',{timeZone:'America/Bahia',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
  const get=type=>dateParts.find(p=>p.type===type).value;$('#schedule-start').value=`${get('year')}-${get('month')}-${get('day')}`;
  $('#update-schedule').onclick=()=>{if(scheduleRecord)loadSchedule(scheduleRecord,false);};
  $('#schedule-complexity').onchange=()=>{if(scheduleRecord)loadSchedule(scheduleRecord,true);};
  $('#download-flow').onclick=()=>{const svg=$('#flowchart svg');if(!svg||!scheduleResult)return;download(`fluxograma-buildbrief-v${scheduleRecord}.svg`,new XMLSerializer().serializeToString(svg),'image/svg+xml;charset=utf-8');};
  $('#download-schedule').onclick=()=>{if(scheduleResult)download(`cronograma-buildbrief-v${scheduleRecord}.md`,planningMarkdown());};
}
