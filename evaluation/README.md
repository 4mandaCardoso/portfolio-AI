# Avaliação reproduzível

Execute na raiz: `python evaluation/run.py`.

## Métricas

- **Recall@3:** quantidade de lugares relevantes presentes nos três primeiros dividida pelo número de relevantes anotados.
- **MRR@3:** média do inverso da posição do primeiro relevante; zero quando não aparece nos três primeiros.
- **Latência:** tempo local da chamada de busca, não inclui rede/frontend. No primeiro acesso semântico pode incluir inicialização e download.

## Amostra

Seis consultas curadas, com um relevante por consulta. Os termos são próximos da base e foram definidos ao construir o protótipo. Não constituem holdout independente. O script também gera cinco planos por template e valida o formato; não mede qualidade de LLM.

Para uma avaliação melhor: colete 30–50 consultas independentes, inclua intenções ambíguas e sem resposta, faça relevância manual sem olhar o ranking, compare keyword/semantic com os mesmos filtros e registre falhas. Não ajuste parâmetros repetidamente no conjunto final de teste.

O resultado padrão é ignorado pelo Git para evitar versionar datas/latências locais sem intenção. Se desejar compartilhar um relatório, revise-o e copie para um arquivo versionado com descrição do ambiente. Não invente métricas quando não executar o experimento.
