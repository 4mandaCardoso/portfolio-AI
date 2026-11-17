---
language:
- pt
- en
license: apache-2.0
base_model: Qwen/Qwen2.5-0.5B-Instruct
pipeline_tag: text-generation
tags:
- lora
- fine-tuning
- educational
---

# Cacau Trip / BuildBrief · experimento de domínio

Fine-tuning supervisionado de uma LLM compacta para conversas sobre os dois protótipos de software. Verifique o manifesto do experimento para confirmar status, passos e métricas reais antes de publicar este card.

## Base e adaptação

Qwen/Qwen2.5-0.5B-Instruct, adaptado por LoRA nativo em PyTorch nas projeções q/v. Os pesos distribuídos no pacote original são somente adaptadores e exigem o carregador fornecido. O diretório produzido por `export_hf.py` contém os pesos fundidos compatíveis com Transformers.

## Dataset

48 exemplos sintéticos autorais de treinamento e 8 de avaliação, em português, sem conversas privadas. Os assuntos incluem requisitos, revisão, cronogramas, rotas, preços simulados e ausência de dados atuais. Não houve anotação humana especializada ou coleta independente.

## Avaliação

Consulte `training_manifest.json` após a exportação ou `ml/artifacts/domain-lora/manifest.json` no projeto. Os campos `eval_loss_before` e `eval_loss_after` medem a previsão de respostas de referência em oito exemplos; `comparison.json` contém duas gerações antes/depois. Não foi realizado benchmark independente nem avaliação de uso em produção.

## Limitações

Modelo pequeno, base multilíngue com adaptação limitada em português, dados poucos e sintéticos. Pode produzir português incorreto, repetir frases e inventar fatos. Não usar para decisões de segurança, atendimento de emergência ou dados atuais. O ajuste não cria um banco de preços, clima ou horários. As ferramentas do aplicativo mantêm validação e a fonte de verdade.

## Autoria e transparência

Experimento de portfólio preparado com assistência de IA para Amanda Cardoso Lopes. Revise e personalize os créditos conforme sua contribuição efetiva. Preserve os créditos e a licença da base. Não afirmar pré-treinamento do zero nem melhora geral de qualidade com base somente em loss menor.
