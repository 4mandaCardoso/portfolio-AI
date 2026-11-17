# Resultados reais do experimento

## Adaptador selecionado para a aplicação

- Base: Qwen/Qwen2.5-0.5B-Instruct.
- Revisão da base: 7ae557604adf67be50417f59c2c2f167def9a775.
- Método: SFT com LoRA nativo, rank 8, alpha 16.
- Parâmetros ajustados: 540,672.
- Atualizações do otimizador: 24.
- Exemplos: 48 treino, 8 avaliação.
- Loss de avaliação antes: 3.068607.
- Loss de avaliação depois: 2.676055.
- Redução relativa de loss: 12.79%. **Não é ganho de acurácia.**
- Execução: CPU, 4 threads, float32, 70.06 segundos após o carregamento do modelo.

As respostas brutas em `artifacts/domain-lora/comparison.json` ainda apresentam imprecisões. O ajuste tornou algumas respostas menos afirmativas, mas não aprendeu corretamente todos os conceitos. Não há evidência suficiente para declarar melhora geral de utilidade, português ou factualidade.

## Primeiro experimento preservado

Base: HuggingFaceTB/SmolLM2-135M-Instruct. Loss: 3.287437 → 2.693144. Apesar da redução, as respostas mostraram repetição e conceitos incorretos. Esse resultado permanece em `artifacts/smollm-baseline`, sem seleção de exemplos favoráveis.

## Tentativa de execução BF16

A tentativa Qwen em BF16 foi interrompida antes de registrar atualizações de otimizador, por baixa velocidade nessa CPU. Não é apresentada como modelo treinado. A execução concluída usa float32; a interrupção está documentada em `artifacts/qwen-bf16-attempt.json`.

## Limites da avaliação

Os oito exemplos foram criados junto com os temas do dataset, e a base foi escolhida após observar resultados. Portanto, esta é uma avaliação exploratória de desenvolvimento, não teste final independente. Loss supervisionado mede ajuste às respostas de referência, não qualidade de uma conversa real. As duas gerações usam decodificação gulosa e limite de 90 tokens; texto e métricas não foram editados.

## Próxima etapa

Ampliar e revisar os dados, separar conjuntos por família de intenção, avaliar respostas com rubrica humana e usar um conjunto final que não participe da escolha da base ou dos hiperparâmetros. Até lá, manter o modelo opcional e experimental e preservar as ferramentas determinísticas como fonte de verdade.
