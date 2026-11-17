# LLM de domínio · fine-tuning supervisionado com LoRA

Este experimento ajusta uma LLM compacta para responder, em português, perguntas sobre Cacau Trip e BuildBrief. É diferente de escrever um prompt ou alimentar uma base de busca: **o otimizador modifica efetivamente os pesos do adaptador**.

## Estado real do experimento

Após uma execução bem-sucedida, `artifacts/domain-lora/` contém:

- `adapter.safetensors`: matrizes treinadas, sem código executável.
- `manifest.json`: modelo base, revisão, hiperparâmetros, passos, versões e perdas de avaliação antes/depois.
- `training_log.jsonl`: perda de treino por atualização e tempo decorrido.
- `comparison.json`: respostas determinísticas de avaliação antes/depois, sem edição manual.

O arquivo `manifest.json` só é gravado com `status=trained` após concluir treinamento, avaliar e verificar que as matrizes B foram atualizadas. A existência do script isoladamente não é evidência de treino. Uma redução de loss não prova qualidade factual ou utilidade em produção.

## Modelo e escolha

Base selecionada: [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct), aproximadamente 0,49 bilhão de parâmetros, com suporte a português e licença Apache 2.0. Foi usada em um ajuste local pequeno. O primeiro experimento com SmolLM2-135M-Instruct permanece preservado por mostrar limitações importantes. Veja RESULTADOS.md antes de interpretar as métricas.

É **fine-tuning de uma base pública**, não pré-treinamento do zero. Não substitui o modelo original, não elimina alucinações e não deve ser apresentado como equivalente a modelos maiores.

## O que LoRA faz

Os pesos originais W ficam congelados. Para cada projeção selecionada:

`saída = W(x) + (alpha / rank) * B(A(x))`

Somente A e B recebem gradientes. A começa aleatória e B começa zerada; antes do treino, a contribuição extra é zero. O script adapta `q_proj` e `v_proj`. A implementação está em `lora.py`, usando PyTorch diretamente; **não é um checkpoint PEFT padrão**. O carregamento é feito pelo módulo fornecido ou pela exportação fundida para Transformers.

## Dados

`build_dataset.py` gera 48 exemplos de treino e 8 de avaliação, todos sintéticos e autorais, criados com assistência de IA. Eles ensinam o comportamento e os limites dos produtos, com perguntas em português. Não usam mensagens privadas dos usuários, preços reais nem dados pessoais sensíveis.

Cada linha JSONL contém uma conversa system → user → assistant. Perguntas idênticas são bloqueadas entre treino e avaliação. Há temas relacionados entre as divisões: isso é uma avaliação exploratória pequena, **não um teste independente de generalização**. A foto de Amanda não participa do treinamento.

## Executar treinamento

Use Python 3.11+ com versão de PyTorch compatível. O ambiente da entrega pode ter uma versão de Python mais recente; consulte `manifest.json` para as versões realmente usadas.

```powershell
python -m venv .venv-llm
.\.venv-llm\Scripts\python.exe -m pip install -r ml/requirements.txt
.\.venv-llm\Scripts\python.exe -X utf8 ml/build_dataset.py
.\.venv-llm\Scripts\python.exe -X utf8 ml/train.py --max-steps 24 --epochs 2
```

O modelo base é baixado para `.model-cache/`, ignorado pelo Git e fora do ZIP distribuído. Reservar memória, espaço e tempo de CPU; não fechar aplicativos do usuário automaticamente. O script interrompe o início se houver menos de 1 GB disponível. O pico real pode ser maior.

Parâmetros padrão: CPU, quatro threads, rank 8, alpha 16, AdamW, taxa 0,0002, batch de um exemplo com acumulação de dois, limite de 192 tokens e seed 42. O log registra o número efetivo de atualizações; `max-steps` pode encerrar antes de todas as épocas.

O loss supervisiona somente a resposta do assistente; os tokens do prompt recebem rótulo -100. Contexto maior que metade da janela é cortado à esquerda para reservar espaço à resposta. A avaliação usa loss ponderado pela quantidade de tokens supervisionados e geração gulosa em duas perguntas separadas.

## Usar nos dois chatbots

```powershell
.\.venv-llm\Scripts\python.exe iniciar.py
```

Abra o chat e escolha **LLM ajustada com LoRA** no seletor Motor da conversa. Os pesos são carregados somente no primeiro uso. A interface identifica o modo como experimental. As sugestões de lugares, as contas, a rota e os prazos continuam vindo das ferramentas de software; o modelo não substitui essas fontes de verdade.

O modo via API permanece separado, configurado no `.env`. O modelo local não foi ajustado para gerar o JSON completo de planejamento: ele serve à conversa. Não ative uma promessa de geração estruturada que o experimento não validou.

## Melhorar a avaliação

- Coletar exemplos adicionais revisados por pessoas.
- Separar cenários por família de intenção, além de perguntas diferentes.
- Avaliar aderência ao contexto, português, alucinações, recusas corretas e ações indevidas.
- Comparar com a base usando os mesmos prompts, geração e rubrica.
- Publicar resultados ruins e bons, sem selecionar apenas demonstrações favoráveis.
- Preferir um modelo multilíngue maior quando houver recursos, mantendo dados de teste intactos.

## Exportar para Hugging Face

`export_hf.py` funde as matrizes no modelo base e grava um diretório compatível com Transformers:

```powershell
.\.venv-llm\Scripts\python.exe -X utf8 ml/export_hf.py --output runtime/modelo-fundido
```

Esse diretório é muito maior que o adaptador. Revise o model card e faça o upload manual em um repositório da sua conta no Hugging Face. Nenhum upload é realizado automaticamente e nenhuma conta foi criada. Preserve a licença da base e descreva dados, limites e métricas reais. O código do projeto usa MIT; o modelo base e seus derivados exigem observar Apache 2.0.

## Como descrever no currículo

Após confirmar o treino, uma descrição fiel é: “Implementei um experimento de SFT com adaptadores LoRA sobre uma LLM compacta, com exemplos sintéticos em português, supervisão de tokens de resposta, avaliação antes/depois e inferência integrada a dois chatbots.”

Não afirmar treinamento do zero, qualidade de produção, revisão humana do dataset ou melhora geral sem evidência.
