# Roteiro de apresentação e estudo

## Cacau Trip · 90 segundos

1. **Problema:** organizar um passeio que combine interesses, tempo e orçamento.
2. **Demonstração:** clique no mapa, busque literatura, selecione duas paradas e ajuste os gastos.
3. **Regra:** diminua orçamento/tempo para demonstrar os alertas.
4. **Técnica:** Haversine filtra proximidade, ranking combina relevância e distância, cálculo é determinístico.
5. **IA:** mostre qual modo está ativo. Só diga embeddings ou LLM se realmente os configurou e executou.
6. **Limite:** a base é pequena, coordenadas aproximadas e custos simulados; há cálculo de deslocamento, mas não de gasto de transporte, e não há classificação de segurança.
7. **Evolução:** dados verificados, rotas reais e avaliação independente de recomendação.

## BuildBrief · 90 segundos

1. **Problema:** transformar uma ideia vaga em um plano revisável.
2. **Demonstração:** gere um plano da pousada e mostre as referências RF → US/Tarefa.
3. **Revisão:** retire pagamentos, carregue a versão anterior e exporte Markdown.
4. **Técnica:** contrato JSON, validação de campos/referências e persistência imutável por versão.
5. **IA:** explique a diferença entre template e integração generativa.
6. **Limite:** formato correto não significa requisito correto; a pessoa precisa revisar.
7. **Evolução:** comparador de versões e avaliador de cobertura de requisitos.

## Perguntas para se preparar

- Por que não calcular tempo de caminhada pela distância em linha reta?
- Como impedir que a LLM invente um estabelecimento? O que a validação atual não consegue impedir?
- Por que usar uma base pequena e mostrar a procedência?
- Qual a diferença entre palavras-chave e embeddings?
- O que Recall@3 mede e por que seis perguntas não bastam para validar o produto?
- Como o histórico preserva a versão anterior?
- Por que uma tarefa precisa apontar para um requisito?
- O que faltaria para atender vários usuários pela internet?

## Como descrever sua contribuição

Seja fiel ao que você executou: base criada com assistência de IA, depois estudada, personalizada e testada por você. Mostre as mudanças reais que fizer. Não alegue que desenvolveu tudo sozinha nem apresente uma demonstração por template como treinamento de modelo.


## Experimento de LLM

Mostre a diferença entre regra, chamada de API e ajuste de pesos. Apresente o dataset, o mascaramento dos tokens do prompt, a base congelada, os adaptadores LoRA, o log e a avaliação antes/depois. Não conclua qualidade só porque o loss diminuiu: as respostas brutas do primeiro experimento mostram repetição. Explique como isso motivou a comparação com uma base multilíngue e por que a avaliação ainda é exploratória.
