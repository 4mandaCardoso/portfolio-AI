"use strict";
let point={lat:-14.8004,lon:-39.0331}, selected=[], currentPlaces=[], latestPlan=null;
let map=null, originMarker=null, markers=null, searchVersion=0, planVersion=0;
const moneyRange = (values) => values.map(money).join(' – ');
function initMap(){
  if(!window.L){
    $('#map').className='map-fallback';
    $('#map').textContent='O mapa precisa de internet para carregar. As sugestões continuam disponíveis a partir do centro de Ilhéus.';
    return;
  }
  map=L.map('map').setView([point.lat,point.lon],15);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
  originMarker=L.circleMarker([point.lat,point.lon],{radius:10,color:'#172d30',fillColor:'#d5ef91',fillOpacity:1}).addTo(map).bindPopup('Seu ponto inicial');
  markers=L.layerGroup().addTo(map);
  map.on('click',event=>{point={lat:event.latlng.lat,lon:event.latlng.lng};originMarker.setLatLng(event.latlng);setCoordinates();invalidateExplanation();updateMapLink();search();});
}
function setCoordinates(){ $('#coordinates').textContent=`Ponto escolhido: ${point.lat.toFixed(5)}, ${point.lon.toFixed(5)} · distâncias em linha reta, coordenadas dos locais aproximadas.`; }
function payload(){
  return {...point,stops:selected.map(p=>({id:p.id,duration:p.duration,cost_min:p.cost_min,cost_max:p.cost_max})),
    group:$('#group').value,budget:$('#budget').value,minutes:$('#minutes').value,interests:$('#interests').value};
}
async function search(){
  const version=++searchVersion;
  message('Buscando na base local…'); $('#search-button').disabled=true;
  try{
    const result=await api('/api/tourism/search',{...point,radius:$('#radius').value,interests:$('#interests').value});
    if(version!==searchVersion)return;
    currentPlaces=result.places;
    $('#search-mode').textContent=result.mode==='semantic'?'Busca por embeddings':'Busca por palavras + proximidade';
    $('#result-count').textContent=`${currentPlaces.length} lugares na base`;
    renderPlaces();message(currentPlaces.length?'Escolha as paradas que combinam com você.':'Nenhum local cadastrado neste raio. Amplie a busca ou escolha outro ponto.');
  }catch(error){if(version===searchVersion)message(error.message,true);}
  finally{if(version===searchVersion)$('#search-button').disabled=false;}
}
function renderPlaces(){
  const root=$('#results'); root.replaceChildren(); if(markers)markers.clearLayers();
  if(!currentPlaces.length)root.append(el('p','Nenhum lugar encontrado na base inicial.','muted'));
  currentPlaces.forEach(place=>{
    const card=el('article',null,'place-card');
    const top=el('div',null,'row between');top.append(el('span',place.tags.slice(0,2).join(' · '),'tag-line'),el('span',`${place.distance_km.toFixed(2)} km`,'pill'));
    card.append(top,el('h3',place.name),el('p',place.description),el('p',place.reason,'tiny'));
    const details=el('details');details.append(el('summary','Dados, fonte e limitações'));
    details.append(el('p',place.data_status),el('p',place.source_scope));
    const source=el('a',`Fonte consultada em ${place.review_date} ↗`); source.href=place.source;source.target='_blank';source.rel='noopener noreferrer';details.append(source);card.append(details);
    const bottom=el('div',null,'card-bottom');bottom.append(el('span',`${place.visit_minutes.join('–')} min · simulação`,'tiny muted'));
    const button=el('button',selected.some(p=>p.id===place.id)?'Adicionado ✓':'+ Adicionar','small');
    button.disabled=selected.some(p=>p.id===place.id);
    button.onclick=()=>{
      selected.push({...place,duration:place.visit_minutes[0],cost_min:place.sample_cost[0],cost_max:place.sample_cost[1]});
      invalidateExplanation();renderStops();renderPlaces();calculate();
    };
    bottom.append(button);card.append(bottom);root.append(card);
    if(markers){
      const popup=el('div');popup.append(el('strong',place.name),el('p','Localização aproximada. Confira no serviço de mapas.'));
      L.circleMarker([place.lat,place.lon],{radius:7,color:'#256a51',fillColor:'#256a51',fillOpacity:.8}).bindPopup(popup).addTo(markers);
    }
  });
}
function invalidateExplanation(){latestPlan=null;$('#explanation').classList.add('hidden');invalidateRoute();}
function renderStops(){
  $('#stop-count').textContent=`${selected.length} parada${selected.length===1?'':'s'}`;
  const root=$('#stops');root.replaceChildren();
  if(!selected.length){root.append(el('p','Adicione lugares para começar.','muted'));}
  selected.forEach((place,index)=>{
    const section=el('div',null,'stop'), title=el('div',null,'stop-title'), actions=el('div',null,'row');
    title.append(el('strong',`${index+1}. ${place.name}`));
    [['↑',-1],['↓',1]].forEach(([label,delta])=>{
      const button=el('button',label,'secondary small');button.type='button';button.setAttribute('aria-label',`Mover ${place.name} ${delta<0?'para cima':'para baixo'}`);
      button.disabled=index+delta<0||index+delta>=selected.length;
      button.onclick=()=>{[selected[index],selected[index+delta]]=[selected[index+delta],selected[index]];invalidateExplanation();renderStops();calculate();};actions.append(button);
    });
    const remove=el('button','Remover','danger small');remove.onclick=()=>{selected=selected.filter(p=>p.id!==place.id);invalidateExplanation();renderStops();renderPlaces();calculate();};actions.append(remove);title.append(actions);section.append(title);
    const fields=el('div',null,'stop-fields');
    [['duration','Visita (min)',5,720],['cost_min','R$ mínimo / pessoa',0,100000],['cost_max','R$ máximo / pessoa',0,100000]].forEach(([key,label,min,max])=>{
      const field=el('div'), input=el('input'); input.type='number';input.min=min;input.max=max;input.value=place[key];input.id=`${place.id}-${key}`;
      const lab=el('label',label);lab.htmlFor=input.id;field.append(lab,input);fields.append(field);
      input.onchange=()=>{place[key]=input.value;invalidateExplanation();calculate();};
    });section.append(fields);root.append(section);
  });
  updateMapLink();
}
function updateMapLink(){
  const a=$('#directions');a.classList.toggle('hidden',!selected.length);
  if(!selected.length)return;
  const params=new URLSearchParams({api:'1',origin:`${point.lat},${point.lon}`,destination:selected.at(-1).name+', Ilhéus, BA'});
  if(selected.length>1)params.set('waypoints',selected.slice(0,-1).map(p=>p.name+', Ilhéus, BA').join('|'));
  a.href='https://www.google.com/maps/dir/?'+params.toString();
}
async function calculate(){
  const version=++planVersion;latestPlan=null;
  try{
    const result=await api('/api/tourism/plan',payload());
    if(version!==planVersion)return null;
    latestPlan=result;const root=$('#totals');root.replaceChildren();
    if(!selected.length)return result;
    const metrics=el('div',null,'metrics');
    [[`${result.visit_minutes} min`,'Somente visitas'],[moneyRange(result.cost_person),'Simulação / pessoa'],[moneyRange(result.cost_group),`Simulação / ${result.group} pessoa(s)`]].forEach(([value,label])=>{
      const metric=el('div',null,'metric');metric.append(el('strong',value),el('span',label));metrics.append(metric);
    });root.append(metrics);
    const list=el('ul',null,'notice clean');result.warnings.forEach(w=>list.append(el('li',w)));root.append(list);
    updateMapLink();return result;
  }catch(error){if(version===planVersion){$('#totals').replaceChildren(el('p',error.message,'notice'));message(error.message,true);}return null;}
}
$('#filters').onsubmit=async event=>{event.preventDefault();await search();invalidateExplanation();await calculate();};
['budget','group','minutes'].forEach(id=>$('#'+id).addEventListener('change',()=>{invalidateExplanation();calculate();}));
$('#reset-point').onclick=()=>{point={lat:-14.8004,lon:-39.0331};if(map){map.setView([point.lat,point.lon],15);originMarker.setLatLng([point.lat,point.lon]);}setCoordinates();invalidateExplanation();search();updateMapLink();};
$('#calculate').onclick=()=>calculate();
$('#export').onclick=async()=>{
  const p=await calculate();if(!p||!p.stops.length)return message('Selecione ao menos uma parada.',true);
  const lines=['# Meu roteiro · Cacau Trip','','Protótipo: valores ilustrativos; transporte não incluído.','',`Visitas: ${p.visit_minutes} min`,`Simulação por pessoa: ${moneyRange(p.cost_person)}`,`Simulação do grupo: ${moneyRange(p.cost_group)}`,''];
  p.stops.forEach((s,i)=>lines.push(`${i+1}. ${s.name} — ${s.duration} min — ${moneyRange([s.cost_min,s.cost_max])} / pessoa`));
  lines.push('','## Limitações',...p.warnings.map(w=>'- '+w));download('roteiro-cacau-trip.md',lines.join('\n'));message('Roteiro exportado.');
};
$('#explain').onclick=async()=>{
  const button=$('#explain');button.disabled=true;message('Preparando explicação…');
  const version=planVersion;
  try{const result=await api('/api/tourism/explain',{...payload(),use_llm:$('#use-llm').checked});
    if(version!==planVersion)return message('O roteiro mudou durante a geração. Gere a explicação novamente.');
    $('#explanation').textContent=(result.mode==='llm'?'LLM conectada · revise as informações\n\n':'Demonstração por template\n\n')+result.explanation;$('#explanation').classList.remove('hidden');message('Explicação pronta.');
  }catch(error){message(error.message,true);}finally{button.disabled=false;}
};
initMap();setCoordinates();setupMode();search();

// Roteamento real separado do cálculo de custos; uma rota antiga nunca permanece após mudar as paradas.
let activeRoute=null,routeLayer=null,routeGeneration=0;
const stopPins=map?L.layerGroup().addTo(map):null;
function invalidateRoute(){
  routeGeneration++;activeRoute=null;
  if(routeLayer&&map){map.removeLayer(routeLayer);routeLayer=null;}
  $('#route-summary').classList.add('hidden');$('#route-summary').replaceChildren();
  $('#route-status').textContent='Paradas ou preferências atualizadas. Clique em Traçar rota pelas ruas.';
  $('#route-status').classList.remove('error');
}
const originalRenderStops=renderStops;
renderStops=function(){originalRenderStops();if(stopPins){stopPins.clearLayers();selected.forEach((p,i)=>L.marker([p.lat,p.lon],{icon:L.divIcon({className:'route-stop-icon',html:String(i+1),iconSize:[30,30],iconAnchor:[15,15]})}).bindPopup(el('span',`${i+1}. ${p.name} · localização aproximada`)).addTo(stopPins));}};
const originalCalculate=calculate;
calculate=async function(){const result=await originalCalculate();if(result&&activeRoute)renderRouteSummary(activeRoute,result);return result;};
function renderRouteSummary(routeResult,plan){
  const root=$('#route-summary');root.classList.remove('hidden');root.replaceChildren(el('h3','Caminhos que conectam seu passeio.'));
  const metrics=el('div',null,'metrics');
  const total=plan.visit_minutes+routeResult.travel_minutes;
  [[(routeResult.distance_m/1000).toFixed(2)+' km','Pelas ruas e caminhos'],[routeResult.travel_minutes.toFixed(1)+' min',`Deslocamento · ${routeResult.profile_label}`],[total.toFixed(1)+' min','Visitas + deslocamento']].forEach(([v,k])=>{const card=el('div',null,'metric');card.append(el('strong',v),el('span',k));metrics.append(card);});root.append(metrics);
  routeResult.legs.forEach((leg,i)=>{const item=el('div',null,'route-leg'),text=el('div');text.append(el('div',`${leg.from} → ${leg.to}`),el('span',`${(leg.distance_m/1000).toFixed(2)} km · ${leg.duration_minutes} min`));item.append(el('strong',String(i+1)),text);root.append(item);});
  if(total>plan.available_minutes)root.append(el('p','O roteiro completo ultrapassa o tempo disponível. Remova paradas ou aumente o tempo.','notice'));
  root.append(el('p','Estimativa sem trânsito em tempo real. Transporte não incluído no gasto. Coordenadas aproximadas; confira os acessos.','tiny muted'));
  const detail=el('details');detail.append(el('summary','Origem e limitações da rota'));routeResult.warnings.forEach(w=>detail.append(el('p',w,'tiny muted')));detail.append(el('p',routeResult.provider,'tiny muted'));root.append(detail);
}
$('#trace-route').onclick=async()=>{
  if(!selected.length)return message('Adicione pelo menos uma parada para traçar a rota.',true);
  const button=$('#trace-route');button.disabled=true;
  invalidateRoute();const version=routeGeneration;
  $('#route-status').textContent='Consultando os caminhos reais entre as paradas…';
  try{const result=await api('/api/tourism/route',{...payload(),profile:$('#route-profile').value});
    if(version!==routeGeneration)return;
    activeRoute=result;
    if(map){
      // GeoJSON é retornado pelo serviço de ruas; não são linhas retas entre os pontos.
      routeLayer=L.geoJSON(result.geometry,{style:{color:'#e8610a',weight:6,opacity:.9,lineCap:'round'}}).addTo(map);
      map.fitBounds(routeLayer.getBounds(),{padding:[35,35],maxZoom:17});
    }
    const plan=await calculate();if(plan)renderRouteSummary(result,plan);
    $('#route-status').textContent=map?'Rota conectada pelas ruas · '+result.profile_label:'Rota consultada. A geometria não pôde ser exibida porque o mapa não carregou.';
  }catch(error){if(version===routeGeneration){$('#route-status').textContent=error.message;$('#route-status').classList.add('error');}}
  finally{button.disabled=false;}
};
$('#route-profile').onchange=()=>invalidateRoute();
function addPlaceFromChat(place){
  if(selected.some(p=>p.id===place.id))return message('Esse lugar já está no seu roteiro.');
  if(selected.length>=10)return message('O protótipo permite até dez paradas.',true);
  selected.push({...place,duration:place.visit_minutes[0],cost_min:place.sample_cost[0],cost_max:place.sample_cost[1]});
  invalidateExplanation();renderStops();renderPlaces();calculate();message(`${place.name} adicionado ao roteiro.`);
}
const cacauChat=initChat({project:'tourism',title:'Assistente Cacau',
  welcome:'Olá! Me conte o que você quer descobrir em Ilhéus e quanto deseja gastar. Posso sugerir lugares cadastrados, ajudar com o roteiro e explicar as rotas. Os valores iniciais são simulações.',
  prompts:['Tenho R$ 120 e gosto de história','Quero opções mais econômicas','Como criar uma rota?'],
  context:()=>({context:{...payload(),radius:$('#radius').value}}),
  addPlace:addPlaceFromChat,setBudget:value=>{$('#budget').value=value;invalidateExplanation();calculate();}
});
$('#open-cacau-chat').onclick=()=>cacauChat.open();$('#mobile-chat').onclick=()=>cacauChat.open();
$('#export').onclick=async()=>{
  const p=await calculate();if(!p||!p.stops.length)return message('Selecione pelo menos uma parada.',true);
  const lines=['# Meu roteiro · Cacau Trip','',`Visitas: ${p.visit_minutes} min`,`Faixa simulada por pessoa: ${moneyRange(p.cost_person)}`,`Faixa simulada do grupo: ${moneyRange(p.cost_group)}`,''];
  p.stops.forEach((s,i)=>lines.push(`${i+1}. ${s.name} — ${s.duration} min — ${moneyRange([s.cost_min,s.cost_max])} / pessoa`));
  if(activeRoute){lines.push('','## Rota pelas ruas',`Modal: ${activeRoute.profile_label}`,`Distância: ${(activeRoute.distance_m/1000).toFixed(2)} km`,`Deslocamento: ${activeRoute.travel_minutes} min`,`Tempo completo: ${(p.visit_minutes+activeRoute.travel_minutes).toFixed(1)} min`,...activeRoute.legs.map(l=>`- ${l.from} → ${l.to}: ${l.duration_minutes} min`));}
  lines.push('','## Limitações',...p.warnings.map(w=>'- '+w),'Valores ilustrativos; gasto de transporte não incluído.');download('roteiro-cacau-trip.md',lines.join('\n'));message('Roteiro exportado.');
};
