# Prompts estruturados e experimentações com LLMs

## Estratégia usada

Os prompts reais estão em `backend/chat.py`, `backend/brief.py` e `backend/server.py`. Cada chamada separa instruções de sistema dos dados de entrada e especifica o papel, a fonte da informação, o formato de saída e os limites. A resposta ainda passa por validação em Python.

## Exemplo 1 · Assistente Cacau

**Papel:** ajudar a explorar os lugares cadastrados.

**Contexto:** roteiro selecionado, candidatos recuperados, orçamento e limitações da base.

**Contrato de API:** objeto JSON com `reply` e `suggestion_ids`. IDs desconhecidos são rejeitados.

**Restrições:** não inventar preços, estabelecimentos, clima ou áreas de risco; não afirmar que alterou ou reservou algo.

Entrada de teste: “Tenho R$ 120 e quero literatura”. A ferramenta recupera os candidatos antes da geração; o modelo não pesquisa livremente na internet. Gastos são simulados.

## Exemplo 2 · BuildBrief

**Papel:** auxiliar a engenharia do planejamento.

**Contexto:** entrada, versão anterior, pedido de revisão e exemplo de estrutura.

**Contrato:** requisitos com IDs, histórias com referência ao requisito e critérios, entidades e tarefas com rastreabilidade.

**Restrições:** registrar dúvidas e suposições, não prometer viabilidade, manter as mudanças revisáveis.

Entrada de teste: “Sistema de reservas de uma pousada, sem pagamentos, para uma primeira versão em uma semana”. Um resultado JSON válido ainda pode ser um planejamento ruim; a revisão de domínio continua necessária.

## Experimentos executados

Os diretórios de `ml/artifacts/` preservam loss, hiperparâmetros e respostas antes/depois de ajustes de bases diferentes. O primeiro ajuste, com SmolLM2, mostrou repetição apesar da queda de loss. Isso motivou a comparação com uma base multilíngue. A seleção é exploratória e não transforma os oito exemplos em teste final independente.

## Experimentos ainda a fazer

Comparar prompts com e sem contexto, com e sem formato estruturado, usando as mesmas perguntas e um modelo fixo. Avaliar português, aderência a fatos, JSON e respeito às restrições. Chamadas de API não foram executadas sem uma chave real; não declarar resultados delas.

Não confundir: prompt fornece instruções na inferência; recuperação fornece dados; fine-tuning modifica parâmetros. O portfólio contém as três estruturas, com estados explícitos.
