# Amanda Cardoso Lopes · Software e Inteligência Artificial

Dois protótipos funcionais, um portfólio com foto, uma página explicando a implementação e um experimento de fine-tuning de LLM com dados, pesos de adaptação e avaliação.

| Projeto | Proposta | Entregas |
| --- | --- | --- |
| **Cacau Trip** | Explorar Ilhéus e montar um passeio personalizado | Mapa, lugares por interesse, paradas, rotas pelas ruas, orçamento e chat |
| **BuildBrief** | Transformar uma ideia em um plano técnico revisável | Requisitos, histórias, tarefas, chat, fluxograma, cronograma e versões |

> Protótipos de portfólio, não produtos em produção. A base turística é pequena, com coordenadas aproximadas e custos simulados. A LLM ajustada é um experimento; métricas, respostas e limitações estão em `ml/`.

## Executar agora

**Todos os projetos, assistentes e experimentos são protótipos educacionais.** A foto é exibida com a identificação abaixo, sem sobreposição.

1. Extraia a pasta inteira.
2. Instale Python 3.11 ou superior, se necessário.
3. Abra o terminal na pasta de `iniciar.py` e execute:

```powershell
python iniciar.py
```

Abra <http://127.0.0.1:8000>. No Windows, também pode usar **INICIAR_WINDOWS.bat**. O modo padrão usa somente a biblioteca padrão; não exige chave de IA nem pip. O mapa e o serviço de rotas exigem internet. Se a porta estiver ocupada: `python iniciar.py --port 8001`.

## Conversar com a LLM ajustada

Use **INICIAR_IA_TREINADA.bat**. O primeiro uso prepara `.venv-llm`, instala bibliotecas e baixa o modelo base. Depois abra o chat e escolha **LLM ajustada com LoRA** em Motor da conversa. A chave de uma API não é necessária para a geração local.

Os adaptadores treinados são pequenos e ficam em `ml/artifacts/`. O modelo base completo não é distribuído no ZIP; será baixado no primeiro uso. Observe memória, conexão e tempo de carregamento. Dados e procedimentos: [ml/README.md](ml/README.md).

## Cacau Trip

1. Clique no mapa para escolher a origem.
2. Informe interesses e raio de busca.
3. Adicione os lugares desejados e ajuste a ordem.
4. Escolha a pé, carro ou bicicleta e clique em **Traçar rota pelas ruas**.
5. Consulte distância, tempo de deslocamento e visitas + deslocamento.
6. Converse com o Assistente Cacau e adicione sugestões pelos cartões.
7. Exporte o roteiro em Markdown.

O backend calcula rotas com OSRM/FOSSGIS e desenha o GeoJSON retornado no Leaflet. Ele não apresenta linhas retas como caminhos reais. O serviço recebe as coordenadas ao traçar, tem política de uso e pode ficar indisponível. Há cache e controle de frequência para uso leve. Não há GPS contínuo ou trânsito em tempo real.

Os dez registros da base trazem fontes e limitações. Preços e durações são simulações, não valores atuais verificados. O gasto de transporte não é calculado. Uma rota não garante segurança ou acessibilidade. Não existem classificações inventadas de bairros perigosos, clima, marés ou parceiros verificados.

## BuildBrief

Descreva a ideia, o público, as tecnologias, o prazo desejado e as restrições. O plano contém requisitos rastreáveis, histórias e critérios, entidades, tarefas, suposições e riscos. O chat recebe a versão aberta e as opções atuais de prazo.

O cronograma permite escolher início, horas por dia e complexidade, além de editar esforço por tarefa. O fluxograma SVG usa as mesmas fases e tarefas e mostra o ciclo de validação. As estimativas pressupõem uma pessoa, sequência de tarefas e dias úteis sem feriados. São heurísticas editáveis, não promessas ou previsões de uma IA treinada em produtividade.

Revisões criam registros no SQLite sem apagar o pai. O chat pode preparar o texto da revisão; a pessoa confirma o salvamento. Exportações: plano Markdown, cronograma Markdown e fluxograma SVG. Ajustes do cronograma são da sessão e devem ser exportados para preservá-los.

## Três motores de conversa

| Motor | Fonte da resposta | Como ativar |
| --- | --- | --- |
| Regras locais | Regras Python e contexto validado | Padrão, sem dependências |
| LLM ajustada com LoRA | Modelo base + adaptadores de domínio | Ambiente de ML e arquivos do experimento |
| LLM via API | Serviço externo compatível | Três campos no `.env` |

A conversa não treina automaticamente o modelo. As sugestões de lugares, as contas, as versões e as rotas continuam validadas por software. O modelo local atende à conversa; não foi validado para gerar sozinho todo o JSON do planejamento.

## Configurar provedor externo, se desejar

Copie `.env.example` para `.env` e preencha:

```dotenv
LLM_BASE_URL=https://ENDERECO-DO-PROVEDOR/v1
LLM_MODEL=IDENTIFICADOR-DO-MODELO
LLM_API_KEY=SUA-CHAVE
RECOMMENDER=keyword
```

Valores ilustrativos: use os dados reais de um provedor compatível com Chat Completions. O programa acrescenta `/chat/completions` à base. Reinicie o servidor. A chave fica no backend. Chamadas podem custar dinheiro e enviam conteúdo ao provedor. Nunca publique `.env` ou mensagens confidenciais.

## Busca por embeddings, opcional

O modo padrão combina palavras e proximidade. Para usar embeddings, instale `requirements-semantic.txt` em ambiente compatível e configure `RECOMMENDER=semantic`. A interface mostra o modo efetivo. Se o download/carregamento falhar, o erro aparece; não há substituição silenciosa. Usar um embedding pronto é diferente do fine-tuning do experimento de conversa.

## Testar e avaliar

```powershell
python -m unittest discover -s tests -v
python evaluation/run.py
```

O teste LoRA é opcional no ambiente leve. No ambiente de ML, execute a mesma suíte com `.venv-llm\Scripts\python.exe`. Ela também verifica inicialização equivalente à base, atualização só do adaptador e equivalência após fusão.

A avaliação de busca usa seis casos curados; é exploratória e próxima da base. O ajuste de LLM usa 48 exemplos sintéticos e oito de avaliação; loss menor não prova melhor qualidade factual. Compare também as respostas brutas e preserve falhas. Veja [validação](docs/VALIDACAO.md).

## Estrutura

| Local | Responsabilidade |
| --- | --- |
| `backend/server.py` | API local e SQLite |
| `backend/tourism.py` | Busca, distância geográfica e cálculo de orçamento |
| `backend/routing.py` | Caminhos reais, perfis, cache e validação |
| `backend/chat.py` | Contexto, regras e ações propostas nos chats |
| `backend/brief.py` | Geração estruturada e validação dos planos |
| `backend/scheduling.py` | Faixas de esforço e calendário |
| `backend/llm.py` | Cliente opcional do provedor externo |
| `backend/local_llm.py` | Carregamento e inferência do adaptador |
| `ml/` | Dados, treino LoRA, pesos, relatórios e model card |
| `web/` | Interfaces responsivas, foto, chat, mapa e SVG |
| `docs/` | Explicações de uso, implementação e apresentação |

## Documentação

- [Passo a passo](docs/PASSO_A_PASSO.md).
- [Novas funções e como foram feitas](docs/NOVIDADES_V2.md).
- [Cacau Trip](docs/ILHEUS_AI.md) — nome do arquivo preservado por compatibilidade.
- [Descrição do BuildBrief](docs/DESCRICAO_BUILDBRIEF.md).
- [Implementação do BuildBrief](docs/BUILDBRIEF.md).
- [Treinamento da LLM](ml/README.md).
- [GitHub e publicação](docs/GITHUB_E_PUBLICACAO.md).

Há também uma página **Como foi feito** dentro do site, com explicação acessível e resultados reais do experimento selecionado.

## Personalizar e publicar

Para publicar os aplicativos completos: [passo a passo de GitHub e Render](docs/HOSPEDAR_RENDER_E_GITHUB.md). O pacote inclui `render.yaml` e uma entrada FastAPI em `backend/webapp.py`. A configuração inicial é leve, sem carregar a LLM treinada. O servidor local `iniciar.py` continua disponível para uso no computador.

Adicione seus links reais em `web/index.html`, confirme a apresentação e estude o código antes de apresentar. Não inventar métricas, competições ou publicação de modelo. Nenhum repositório GitHub ou Hugging Face foi criado automaticamente.

O servidor é local e vinculado a `127.0.0.1`, sem login ou isolamento de usuários. Não o exponha diretamente na internet. Para produção, preparar servidor adequado, autenticação, cotas, política de dados, monitoramento e gestão de segredos. GitHub Pages não executa este backend.

## Autoria e licenças

Base desenvolvida com assistência de IA para estudo e personalização por Amanda Cardoso Lopes. Código MIT, modelo base sob sua licença original, fontes e mapas com atribuições próprias. A foto foi fornecida pela usuária para este portfólio e não faz parte do dataset de treinamento.
