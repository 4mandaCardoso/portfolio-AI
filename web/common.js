"use strict";
const $ = (selector) => document.querySelector(selector);
function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined && text !== null) node.textContent = text;
  if (className) node.className = className;
  return node;
}
async function api(path, data) {
  const response = await fetch(path, data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Falha na solicitação.');
  return result;
}
function message(text, error=false) {
  const target = $('#status');
  target.textContent = text;
  target.classList.toggle('error',error);
}
function download(name, content, type='text/markdown;charset=utf-8') {
  const url = URL.createObjectURL(new Blob([content],{type}));
  const link = el('a'); link.href=url; link.download=name; link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}
const money = (value) => new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0}).format(value);
async function setupMode() {
  try {
    const status = await api('/api/status');
    document.querySelectorAll('.llm-toggle').forEach(input => {input.disabled=!status.llm_configured;});
    document.querySelectorAll('.mode-hint').forEach(node => {node.textContent = status.llm_configured ? 'LLM configurada. Ative para enviar os dados ao seu provedor.' : 'Modo demonstração • configure .env para conectar uma LLM.';});
    return status;
  } catch (error) {message(error.message,true);}
}
