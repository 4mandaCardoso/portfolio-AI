# BuildBrief — Assistente de planejamento de software com IA

## Descrição para o portfólio

Aplicação que transforma ideias em planos técnicos com requisitos rastreáveis, histórias de usuário, critérios de aceitação, tarefas, fluxogramas e estimativas de prazo. Integra um chatbot contextual e permite revisar, versionar e exportar o planejamento. Desenvolvida com Python, JavaScript e SQLite, oferece integração com LLMs, validação estruturada das respostas e um experimento de adaptação LoRA para a conversa.

## Problema que resolve

Uma pessoa pode saber o que deseja construir sem saber como organizar o desenvolvimento. O BuildBrief ajuda a explicitar o público, o escopo, as restrições, as dúvidas e os passos de implementação antes do código.

## Experiência de uso

1. Descrever a ideia e informar público, tecnologias e restrições.
2. Gerar o plano estruturado.
3. Conversar sobre requisitos, dados, critérios, riscos e estimativas.
4. Visualizar a sequência de tarefas em um fluxograma.
5. Ajustar horas por dia, complexidade e esforço.
6. Preparar e confirmar uma revisão, preservando versões anteriores.
7. Exportar o plano, cronograma ou fluxograma.

## Contribuição técnica

- Contratos JSON e validação de referências entre artefatos.
- Persistência transacional de versões em SQLite.
- Interface de chat reutilizada, com contexto específico por projeto.
- Cronograma heurístico editável, com faixas de esforço e calendário de dias úteis.
- Fluxograma SVG construído a partir da mesma estrutura do cronograma.
- Integração opcional com provedor de LLM e com adaptador local de domínio.
- Separação entre texto generativo, regras de negócio e ações confirmadas pela pessoa.

## Limitações honestas

O template é limitado; o modelo local é experimental; os prazos não são promessas. A validação estrutural não garante que os requisitos sejam completos ou corretos. O sistema não programa o produto inteiro nem prevê a produtividade individual. A pessoa revisa e confirma as decisões.
