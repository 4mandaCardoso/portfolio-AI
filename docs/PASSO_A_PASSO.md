# Comece por aqui

## 1. Abrir os projetos

1. Extraia o ZIP inteiro com **Extrair tudo**. Não execute de dentro da janela do ZIP.
2. Abra a pasta `portfolio-ia` no VS Code: Arquivo → Abrir pasta.
3. Abra Terminal → Novo terminal.
4. Digite `python --version`. Se não reconhecer, tente `py --version`. É necessário Python 3.11 ou superior.
5. Execute `python iniciar.py` (ou `py iniciar.py`).
6. Abra o endereço impresso: `http://127.0.0.1:8000`.

O modo padrão não usa pip nem depende de chave paga. Mapa e fontes visuais externas precisam de internet; se o mapa não carregar, os cartões ainda podem funcionar com o ponto inicial padrão. O primeiro acesso à busca semântica opcional baixa um modelo.

## 2. Experimentar Cacau Trip

1. Entre em **Explorar Ilhéus**.
2. Digite `literatura, história e gastronomia`.
3. Clique em um ponto do mapa e ajuste o raio de busca.
4. Adicione três locais. O aplicativo trabalha com dez registros iniciais, não uma busca completa de todos os estabelecimentos.
5. Ajuste minutos e faixa de gasto por pessoa em cada parada. Os valores iniciais são ilustrativos.
6. Altere o orçamento para R$ 10 e observe o alerta de orçamento excedido.
7. Use as setas para reordenar e o botão Remover para excluir uma parada.
8. Clique em **Explicar meu roteiro**. Sem configuração, é uma explicação por template.
9. Clique em **Baixar roteiro**. O arquivo Markdown abre no VS Code.
10. Se desejar, abra as paradas no Maps. Confira se o serviço reconheceu cada destino e preservou a ordem; limites de paradas variam entre plataformas.

**Rotas nesta versão:** após selecionar as paradas, escolha o modal e clique em Traçar rota pelas ruas. O mapa conecta as paradas com GeoJSON retornado pelo serviço OSRM/FOSSGIS. Distância e deslocamento são mostrados e somados às visitas. Mudar as paradas invalida a rota. Não há trânsito em tempo real, preço atual, previsão de lotação ou classificação de áreas perigosas.

## 3. Experimentar BuildBrief

1. Abra **BuildBrief**.
2. Use o exemplo de pousada ou escreva outra ideia.
3. Preencha público, prazo, tecnologias e restrições.
4. Gere o planejamento. O modo aparece no resultado.
5. Leia requisitos, histórias, critérios de aceitação, entidades e tarefas.
6. Peça `retire os pagamentos online` e salve a revisão.
7. Observe a nova versão e carregue a antiga pelo histórico: a anterior permanece preservada.
8. Baixe Markdown.

O template reconhece reservas, roteiros, produtos, tarefas e chamados por palavras. Pedidos arbitrários de revisão são registrados como pendências. Para interpretação generativa, conecte uma LLM via API. Há também um adaptador LoRA local experimental para a conversa; consulte ml/README.md.

## 4. Ligar uma IA real

1. Crie uma cópia de `.env.example` chamada `.env`, na mesma pasta de `iniciar.py`.
2. No serviço de IA da sua escolha, obtenha uma chave, um identificador de modelo e a URL da API compatível com Chat Completions.
3. Preencha os três campos:

```dotenv
LLM_BASE_URL=https://ENDERECO-DO-SEU-PROVEDOR/v1
LLM_MODEL=IDENTIFICADOR-DO-MODELO
LLM_API_KEY=SUA-CHAVE
RECOMMENDER=keyword
```

Os valores acima são exemplos de formato, não credenciais funcionais. A base não deve terminar em `/chat/completions`, pois o programa acrescenta essa parte.

4. Encerre o servidor com Ctrl+C e execute novamente.
5. A caixa **Usar LLM real** ficará habilitada se os três campos estiverem preenchidos. Isso indica configuração presente, não validação antecipada da chave.
6. Ative a caixa e gere. Falhas de autenticação, modelo, rede ou JSON serão mostradas.

As chamadas usam HTTPS. O provedor recebe os textos que você enviar e pode cobrar. A aplicação não armazena a chave no histórico nem envia a chave para o frontend. Não inclua `.env` no GitHub.

## 5. Ligar embeddings

1. Instale Python 3.12 se quiser isolar as dependências de ML.
2. Execute os comandos do README para criar `.venv` e instalar `requirements-semantic.txt`.
3. Configure `RECOMMENDER=semantic` no `.env`.
4. Inicie com o Python da `.venv`.
5. Busque um interesse e confira o indicador **Busca por embeddings**.

Essa é inferência com um modelo pré-treinado, não treinamento próprio. O ranking continua aplicando filtro geográfico.

## 6. Personalizar e apresentar hoje

- Adicione seus links reais em `web/index.html`.
- Confirme suas informações pessoais e de formação.
- Revise as coordenadas em `data/places.json`; marque como verificadas apenas após realmente conferir.
- Execute os testes e a avaliação.
- Grave um vídeo de 60–90 segundos de cada projeto. Há um roteiro em `APRESENTACAO.md`.
- Publique o código seguindo `GITHUB_E_PUBLICACAO.md`.

## Problemas comuns

| Sintoma | Solução |
| --- | --- |
| Python não reconhecido | Instale Python e reabra o terminal, ou tente `py iniciar.py` |
| Porta em uso | `python iniciar.py --port 8001` e abra a nova URL |
| Interface sem resultados | Veja o erro, volte ao centro e amplie o raio |
| Mapa não carregou | Confira internet/CDN; a lista ainda pode usar o centro padrão |
| IA indisponível | Confira os três campos e reinicie; não exponha sua chave |
| Falha nos embeddings | Use `keyword` ou confira ambiente Python/dependências/modelo |
| Mensagem de origem | Abra `127.0.0.1`, não um arquivo HTML por duplo clique |
| Histórico vazio em outro computador | O histórico está no SQLite local, não na nuvem |

## Seus dados locais

O histórico fica em `runtime/briefs.sqlite3`. Essa pasta nasce ao usar BuildBrief e é ignorada pelo Git. Fechar o navegador não apaga o histórico. Para limpar, pare o servidor e remova somente esse arquivo, se desejar; isso apaga as versões locais. Não coloque ideias confidenciais no repositório.


## 7. Chat, fluxogramas e estimativas

Os dois projetos possuem um botão de assistente no canto inferior. No chat, escolha o motor: regras locais, LLM ajustada com LoRA ou provedor via API. Os modos indisponíveis ficam desabilitados. Conversas ficam na sessão do navegador e podem ser limpas. Nunca são usadas automaticamente para treinar.

No BuildBrief, gere um plano para abrir o cronograma. Escolha início e horas por dia; edite esforço mínimo/máximo das tarefas e recalcule. O fluxograma mostra a sequência e o retorno aos ajustes caso os critérios não sejam atendidos. As opções de exportação ficam acima dele.

Para usar os pesos treinados, abra INICIAR_IA_TREINADA.bat. Ele prepara o ambiente de ML e usa o adaptador presente em ml/artifacts/domain-lora. O modelo base exige download no primeiro uso. Não é necessário treinar de novo se o pacote já contém o adaptador concluído. Detalhes: docs/NOVIDADES_V2.md e ml/README.md.
