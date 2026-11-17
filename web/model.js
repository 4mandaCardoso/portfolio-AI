"use strict";
async function renderModelInfo(){
  const target=document.querySelector('#model-info');if(!target)return;
  try{const info=await api('/api/model');if(info.status!=='trained'){target.textContent='O experimento ainda não possui um adaptador concluído neste diretório. Consulte ml/README.md.';return;}
    target.replaceChildren(el('span','Fine-tuning concluído · experimento local','pill'),el('h3','Uma LLM compacta ajustada ao domínio.'));
    target.append(el('p',`Base: ${info.base_model}. Adaptadores LoRA em ${info.targets.join(' e ')}.`, 'muted'));
    const metrics=el('div',null,'metrics');
    [[Number(info.trainable_parameters).toLocaleString('pt-BR'),'Parâmetros ajustados'],[`${info.train_examples} / ${info.eval_examples}`,'Exemplos: treino / avaliação'],[`${info.optimizer_steps}`,'Atualizações de otimizador']].forEach(([value,label])=>{const item=el('div',null,'metric');item.append(el('strong',value),el('span',label));metrics.append(item);});target.append(metrics);
    target.append(el('p',`Loss de avaliação: ${info.eval_loss_before.toFixed(3)} antes → ${info.eval_loss_after.toFixed(3)} depois. Dados sintéticos, apenas oito exemplos de avaliação; isso não prova melhora geral de qualidade.`, 'tiny muted'));
    target.append(el('p','Para conversar com o modelo ajustado, inicie pelo INICIAR_IA_TREINADA.bat e selecione a opção LoRA no chat. A base é multilíngue, mas o ajuste pequeno ainda produz imprecisões.','tiny muted'));
  }catch(error){target.textContent=error.message;}
}
renderModelInfo();
