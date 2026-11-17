# Versão 2 · Cacau Trip e BuildBrief

## O que mudou

- Cacau Trip passa a se chamar **Cacau Trip**, com identidade creme, marrom e laranja inspirada nas referências fornecidas.
- Foto de Amanda no portfólio e na navegação do Cacau Trip, preservada sem edição do conteúdo.
- Rotas desenhadas pelas ruas entre o ponto inicial e as paradas escolhidas.
- Chatbot contextual nos dois aplicativos, com histórico da sessão e modos claramente identificados.
- BuildBrief com cronograma editável, faixas de esforço, dias úteis e fluxograma SVG.
- Página **Como foi feito**, disponível na navegação, e documentação técnica ampliada.
- Experimento de fine-tuning LoRA: dados, código, adaptador quando concluído, logs e avaliação antes/depois. O estado efetivo consta em `ml/artifacts/domain-lora/manifest.json`; não confundir código de treino com treino concluído.

## Executar

O modo leve continua em `INICIAR_WINDOWS.bat` ou `python iniciar.py`. Para conversar com o adaptador treinado, use `INICIAR_IA_TREINADA.bat`; a primeira preparação instala dependências e baixa o modelo base. Dentro do chat, escolha **LLM ajustada com LoRA**. O modo só é habilitado quando o adaptador e as dependências estão disponíveis.

## Rotas reais

1. Abra **Cacau Trip**.
2. Escolha um ponto inicial no mapa.
3. Adicione lugares e defina a ordem.
4. Escolha **A pé**, **Carro** ou **Bicicleta**.
5. Clique em **Traçar rota pelas ruas**.

A linha laranja é a geometria GeoJSON retornada pelo OSRM, usando a instância de perfil correspondente do FOSSGIS. A expressão `/driving` no protocolo OSRM não muda o perfil pré-processado do servidor: os prefixos `routed-foot`, `routed-bike` e `routed-car` selecionam o modo correto. O resultado inclui distância, deslocamento e visitas + deslocamento.

Mudar ponto, paradas ou preferências invalida a rota anterior. O protótipo exige um novo clique; não consulta continuamente o serviço público. Há cache de cinco minutos e intervalo mínimo de uma chamada por segundo no backend. Falha do serviço gera erro, nunca uma linha reta disfarçada de trajeto.

O serviço externo recebe as coordenadas solicitadas e pode registrá-las. Não há rastreamento de GPS: a origem é escolhida manualmente no mapa. Leia a política em <https://routing.openstreetmap.de/about.html>. Fontes: dados OpenStreetMap e motor OSRM. Rotas não garantem segurança, acessibilidade, passagem aberta ou precisão de entradas. Não há trânsito ao vivo nem cálculo de gasto com transporte.

## Chatbots

### Três motores

| Motor | Execução | Treinamento neste projeto |
| --- | --- | --- |
| Regras locais | Python, com respostas e recuperação de dados | Nenhum |
| LLM via API | Provedor compatível configurado no `.env` | Não altera os pesos do provedor |
| LLM ajustada com LoRA | Modelo compacto no próprio computador | Fine-tuning supervisionado nos exemplos de `ml/data` |

A conversa é guardada em `sessionStorage`, separada por projeto, limitada às últimas 12 mensagens. **Limpar** remove esse histórico da sessão. Em modo API, a conversa e o contexto são enviados ao provedor. No modo treinado local, a geração ocorre no computador após o download do modelo. Nenhum chat treina automaticamente com mensagens dos usuários.

### Assistente Cacau

Recupera lugares da base e conhece as paradas escolhidas. As sugestões aparecem em cartões; a pessoa decide adicioná-las. Um orçamento mencionado pode ser aplicado por botão. O chat não reserva serviços nem altera o roteiro sem ação da pessoa. Segurança e clima sem dados são tratados por respostas de limite explícito; não por inferência de um modelo.

### Assistente BuildBrief

Recebe o plano aberto e as opções atuais do cronograma. Pode explicar requisitos, critérios, tarefas e prazos. Um pedido de mudança oferece **Preparar revisão no planejamento**. Isso preenche o campo para revisão; a nova versão só nasce após **Salvar nova versão**. A anterior continua no histórico.

## Fluxogramas e possíveis prazos

1. Gere um plano no BuildBrief.
2. Na seção **Visualize o próximo passo**, escolha início, horas por dia e complexidade.
3. Edite horas mínimas/máximas por tarefa.
4. Clique em **Recalcular prazos**.
5. Consulte o fluxograma e exporte SVG ou Markdown.

O cálculo pressupõe uma pessoa e tarefas sequenciais, com trabalho de segunda a sexta, sem descontar feriados. As dependências são hipóteses de planejamento. A complexidade média parte de 4–8 h por tarefa; baixa usa fator 0,5 e alta fator 2. Há descoberta, integração/testes e documentação. São regras editáveis, não estimativas aprendidas com projetos reais.

Datas mínimas e máximas representam dois cenários completos de esforço. As faixas não significam que tarefas dependentes aconteçam em paralelo. O prazo desejado digitado no formulário é contexto; não força o cálculo a caber naquele prazo. Alterações do cronograma ficam na sessão até exportar e não sobrescrevem os requisitos versionados.

O SVG é montado no navegador a partir das fases/tarefas validadas, com textos inseridos como texto. Não utiliza imagens geradas nem executa diagramas arbitrários vindos da LLM. O Markdown exportado inclui um equivalente Mermaid.

## Referências de implementação

- `backend/routing.py`: serviço, cache, perfis e validação de geometria.
- `backend/chat.py`: contexto, limites, regras e propostas de ação.
- `backend/scheduling.py`: esforço, capacidade e calendário.
- `backend/local_llm.py`: inferência opcional do adaptador.
- `ml/lora.py`: atualização de baixo posto dos pesos.
- `ml/train.py`: treinamento, avaliação e registro do experimento.
- `web/chat.js`: interface compartilhada de conversa.
- `web/planning.js`: cronograma e SVG.
- `web/how.html`: explicação acessível dentro do site.

## Escopo das referências visuais

Guias verificados, reciclagem com recompensas, integração Gov.br, carteira, clima e marés em tempo real **não foram implementados**. Não há pontos, parceiros, avaliações ou verificações inventados. O aplicativo apresenta esses temas como evoluções futuras.
