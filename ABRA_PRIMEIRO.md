# Sua versão atualizada

## Ver o portfólio publicado

[Abrir a prévia privada](https://amanda-ia-cacau-buildbrief-17nov.diligentaisle5.chatgpt.site)

O site publicado apresenta os projetos, os resultados do treinamento e o painel de evidências. As demos completas com mapa, chat e inferência local são executadas nesta pasta.

## Abrir os projetos no computador

1. Extraia o ZIP inteiro.
2. Clique em **INICIAR_WINDOWS.bat** para o modo leve, ou **INICIAR_IA_TREINADA.bat** para habilitar a LLM ajustada.
3. Abra **http://127.0.0.1:8000**.
4. No chatbot, escolha o motor desejado. O modo LoRA exige dependências e o download da base no primeiro uso.

## O que testar

- Cacau Trip: adicione lugares → escolha modal → **Traçar rota pelas ruas** → converse com o Assistente Cacau.
- BuildBrief: gere um plano → ajuste horas por dia → veja o fluxograma → converse sobre o prazo e prepare revisões.
- Como foi feito: explicações técnicas e números reais do ajuste.
- Evidências: automação em lote e seus limites.

O adaptador já foi treinado. Não é preciso treinar de novo para utilizá-lo. Pesos e relatórios estão em `ml/artifacts/domain-lora`; o primeiro experimento foi preservado em `smollm-baseline`. O modelo é experimental e ainda apresenta respostas imprecisas.

Leia `README.md`, `docs/NOVIDADES_V2.md`, `ml/README.md` e `ml/RESULTADOS.md` para estudar e apresentar o trabalho. Não há uso por clientes ou horas humanas poupadas comprovadas; o pacote inclui um plano para medir isso de verdade.

## Colocar no GitHub e no Render

Siga `docs/HOSPEDAR_RENDER_E_GITHUB.md`. Para o Render, use `requirements-render.txt` e a entrada `backend.webapp:app`, conforme os comandos do guia. Os arquivos de hospedagem não publicam nada automaticamente na sua conta.
