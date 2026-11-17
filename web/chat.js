"use strict";
function initChat(options){
  let pending=false,version=0,conversation=[];
  const key='portfolio-chat-v2-'+options.project;
  try{const saved=JSON.parse(sessionStorage.getItem(key)||'[]');if(Array.isArray(saved))conversation=saved.filter(m=>m&&['user','assistant'].includes(m.role)&&typeof m.content==='string').slice(-12);}catch{}
  const launcher=el('button','✦ '+options.title,'chat-launcher');launcher.type='button';launcher.setAttribute('aria-expanded','false');launcher.setAttribute('aria-controls','chat-window');
  const panel=el('section',null,'chat-window hidden');panel.id='chat-window';panel.setAttribute('aria-label',options.title);
  const header=el('div',null,'chat-header'),mark=el('span','✦','cocoa-mark'),title=el('div',null,'chat-title');title.append(el('strong',options.title),el('span','Conversa com contexto do projeto'));
  const controls=el('div',null,'chat-top-controls'),clear=el('button','Limpar'),close=el('button','×');clear.type=close.type='button';close.setAttribute('aria-label','Fechar conversa');controls.append(clear,close);header.append(mark,title,controls);
  const log=el('div',null,'chat-log');log.setAttribute('role','log');log.setAttribute('aria-live','polite');
  const prompts=el('div',null,'chat-prompts');options.prompts.forEach(text=>{const b=el('button',text);b.type='button';b.onclick=()=>sendMessage(text);prompts.append(b);});
  const error=el('p','','chat-error');error.setAttribute('role','status');
  const footer=el('div',null,'chat-controls'),toggleLabel=el('label',null,'check'),engine=el('select');engine.id='chat-engine';engine.setAttribute('aria-label','Motor do chatbot');
  [['rules','Regras locais'],['trained','LLM ajustada com LoRA'],['api','LLM via API (.env)']].forEach(([value,label])=>{const option=el('option',label);option.value=value;option.disabled=value!=='rules';engine.append(option);});toggleLabel.append(el('span','Motor da conversa'),engine);
  api('/api/status').then(status=>{engine.querySelector('[value="api"]').disabled=!status.llm_configured;engine.querySelector('[value="trained"]').disabled=!status.trained_model_available;}).catch(()=>{});
  const form=el('form',null,'chat-form'),input=el('input'),send=el('button','➤');input.type='text';input.maxLength=2000;input.required=true;input.placeholder='Pergunte ou conte sua ideia…';input.setAttribute('aria-label','Sua mensagem');send.type='submit';send.setAttribute('aria-label','Enviar mensagem');form.append(input,send);
  footer.append(toggleLabel,form,el('p','LoRA: modelo compacto experimental no seu computador. API: envia a conversa ao provedor configurado. Respostas podem conter erros.','chat-data-note'));
  panel.append(header,log,prompts,error,footer);document.body.append(launcher,panel);
  function bubble(role,text,mode){const node=el('div',null,'chat-bubble'+(role==='user'?' user':''));node.append(el('span',text));if(mode)node.append(el('span',mode==='trained'?'LLM com fine-tuning LoRA · experimental':mode==='llm'?'LLM via API · revise a resposta':'Assistente local · respostas por regras','chat-mode'));log.append(node);log.scrollTop=log.scrollHeight;}
  function persist(){try{sessionStorage.setItem(key,JSON.stringify(conversation.slice(-12)));}catch{}}
  function welcome(){bubble('assistant',options.welcome,'local');}
  if(conversation.length)conversation.forEach(m=>bubble(m.role,m.content));else welcome();
  function open(){panel.classList.remove('hidden');launcher.setAttribute('aria-expanded','true');input.focus();}
  function hide(){panel.classList.add('hidden');launcher.setAttribute('aria-expanded','false');launcher.focus();}
  launcher.onclick=()=>panel.classList.contains('hidden')?open():hide();close.onclick=hide;
  panel.addEventListener('keydown',event=>{if(event.key==='Escape')hide();});
  clear.onclick=()=>{version++;pending=false;send.disabled=false;conversation=[];persist();log.replaceChildren();error.textContent='';welcome();};
  async function sendMessage(text){
    if(pending||!text.trim())return;open();pending=true;send.disabled=true;error.textContent='Preparando resposta…';
    const requestVersion=++version,history=conversation.slice(-12);bubble('user',text);input.value='';
    try{
      const result=await api('/api/chat',{project:options.project,message:text,history,use_llm:engine.value==='api',use_trained:engine.value==='trained',...options.context()});
      if(requestVersion!==version)return;
      conversation.push({role:'user',content:text},{role:'assistant',content:result.reply});conversation=conversation.slice(-12);persist();bubble('assistant',result.reply,result.mode);
      (result.suggestions||[]).forEach(place=>{const card=el('div',null,'chat-suggestion'),desc=el('div');desc.append(el('strong',place.name),el('small',`${money(place.sample_cost[0])}–${money(place.sample_cost[1])} / pessoa · simulação`));const add=el('button','Adicionar','small');add.type='button';add.onclick=()=>{options.addPlace?.(place);add.textContent='Adicionado ✓';add.disabled=true;};card.append(desc,add);log.append(card);});
      if(result.budget_suggestion!==null&&result.budget_suggestion!==undefined&&options.setBudget){const b=el('button',`Aplicar orçamento de ${money(result.budget_suggestion)}`,'secondary small');b.type='button';b.onclick=()=>{options.setBudget(result.budget_suggestion);b.textContent='Orçamento atualizado';b.disabled=true;};log.append(b);}
      (result.actions||[]).forEach(action=>{if(action.type==='revision'&&options.revise){const b=el('button','Preparar revisão no planejamento','small');b.type='button';b.onclick=()=>{options.revise(action);hide();};log.append(b);}});
      log.scrollTop=log.scrollHeight;error.textContent='';
    }catch(err){if(requestVersion===version){error.textContent=err.message;bubble('assistant','Não consegui concluir essa resposta. Sua mensagem não alterou o projeto. Tente novamente.');}}
    finally{if(requestVersion===version){pending=false;send.disabled=false;}}
  }
  form.onsubmit=event=>{event.preventDefault();sendMessage(input.value.trim());};setupMode();return {open};
}
