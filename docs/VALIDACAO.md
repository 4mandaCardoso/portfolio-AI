# Verificação da versão 2

## Código

- Suíte de cálculos, referências, revisões, consultas HTTP em memória e exportação Markdown.
- Testes de geometria de rota, perfil, cache, erro de caminho e coordenadas inválidas.
- Testes dos chats, orçamento, contexto, propostas de revisão e ausência de dados de segurança.
- Testes de cronograma, dias úteis, dependências, capacidade e estimativas inválidas.
- Teste opcional de LoRA: base congelada, inicialização equivalente, atualização efetiva e equivalência após fusão.
- Verificação de sintaxe Python e JavaScript.

## Navegador

Verificados no navegador: foto no portfólio, Cacau Trip carregado, seleção de duas paradas, rota pelas ruas retornada pelo serviço real, resumo de distância e duração, resposta contextual do chat, geração de plano, acentuação, cronograma e fluxograma, alteração de capacidade para quatro horas diárias e resposta do chat com os prazos atuais.

O teste de download de SVG pelo navegador não foi concluído: a permissão de download foi recusada. Não houve tentativa de contornar essa decisão. A renderização do SVG e os geradores de exportação podem ser inspecionados no código; isso não equivale à confirmação do download ponta a ponta.

## LLM

Resultados efetivos ficam nos manifestos e comparações em `ml/artifacts/`. Há um primeiro experimento com SmolLM2, preservado mesmo apresentando repetição nas respostas. Isso demonstra por que redução de loss não basta para alegar qualidade. O adaptador selecionado para a aplicação fica em `domain-lora`; consulte o respectivo manifesto, sem transferir métricas entre bases.

O dataset contém 48 exemplos de treinamento e oito de avaliação, sintéticos e tematicamente relacionados. Não houve avaliação independente de uso em produção nem anotação por especialistas. As respostas brutas foram preservadas, inclusive falhas.

No ambiente de ML, os 21 testes passaram, incluindo o teste de LoRA. A chamada HTTP de inferência local retornou status 200 e modo `trained`; a resposta bruta está em `ml/artifacts/domain-lora/integration_inference.json` e ainda contém imprecisão. A integração funciona, mas isso não certifica qualidade semântica.

A atualização para Render inclui uma entrada FastAPI/Uvicorn. O teste de hospedagem verificou saúde, página inicial, geração/exportação, isolamento do histórico entre dois navegadores, rejeição de origem externa e bloqueio do modelo local no modo leve. Nessa suíte, 22 casos foram executados: 21 passaram e o teste LoRA foi pulado por não haver PyTorch no ambiente web. O LoRA havia sido verificado separadamente no ambiente de ML. Não houve deploy na conta Render da usuária.

O painel privado de portfólio foi publicado e confirmado pelo serviço. Consulte PUBLICACAO.md. O backend dos dois protótipos continua local. Foi aplicada uma correção de largura mínima no layout móvel após detectar transbordamento; o ajuste não teve uma segunda conferência visual concluída.

## Não realizado

Não houve publicação em GitHub/Hugging Face, teste com uma chave paga, treinamento do zero, validação em campo de coordenadas/preços/horários ou certificação de segurança de rotas. Não há promessa de qualidade de produção.
