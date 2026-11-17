# Evidências para o formulário da candidatura

O formulário reúne níveis de experiência. Não é necessário nem coerente afirmar todas as opções: “ainda não tenho portfólio” deixa de descrever sua situação depois que os projetos existem.

| Opção | Evidência disponível | O que ainda falta |
| --- | --- | --- |
| Prompts estruturados e experimentações com LLMs | `prompts/`, contexto validado e experimentos de fine-tuning em `ml/` | Revisar e explicar o que você realmente executou e personalizou |
| Automações que economizaram horas reais | CLI de geração/validação/exportação em lote; tempo automático em `evidence/batch_benchmark.json` | Medir uma tarefa manual equivalente e comparar; ainda não há horas poupadas comprovadas |
| Ferramentas internas deployadas, dashboards ou agentes | Duas ferramentas locais e uma página de evidências | Hospedagem acessível e confirmação do deployment antes de afirmar “deployado” |
| Soluções em produção usadas por outras pessoas, com resultados mensuráveis | Código e instrumentação reproduzível de protótipos | Uso real por pessoas, consentimento quando necessário, período de observação e métricas de resultado |
| Todas as opções acima | Não sustentado por este pacote isoladamente | Não selecionar apenas porque o código existe |

## Como medir economia de tempo de forma honesta

1. Defina um trabalho comparável: por exemplo, cinco planos com o mesmo nível de detalhe.
2. Cronometre a execução manual real, incluindo revisão.
3. Cronometre a execução automatizada, incluindo configuração, correções e revisão.
4. Registre quantas vezes foi realizado e as diferenças de qualidade.
5. Some apenas economias observadas. Não multiplique um exemplo hipotético por meses de uso inexistentes.

O benchmark fornecido mede apenas execução automática com templates sintéticos. Não demonstra horas humanas economizadas.

## Como registrar uso por outras pessoas

Convide pessoas reais para executar uma tarefa clara. Anote versão, data, quantidade de participantes, conclusão da tarefa, tempo e problemas observados. Não publicar identidade ou dados privados sem autorização. Diferencie “teste de usabilidade” de “produção”. Não inventar usuários, depoimentos ou resultados.

## Evidência técnica que você pode demonstrar agora

- Seleção e conexão de paradas em mapa real.
- Geração, revisão e exportação de planos.
- Fluxograma e cronograma com capacidade editável.
- Validações e suíte de testes.
- Treino LoRA, pesos e análise de resultados positivos e negativos.
- Automação local em lote com duração medida.

Uma candidatura forte pode apresentar protótipos bem explicados e limites claros. As experiências de produção precisam corresponder ao que ocorreu fora do código.
