# Cacau Trip · implementação

Nome anterior: Cacau Trip. O arquivo mantém o nome por compatibilidade com links antigos.

## Fluxo de dados

1. Leaflet coleta o ponto escolhido.
2. `POST /api/tourism/search` aplica Haversine e ranking.
3. A pessoa seleciona e ordena paradas.
4. `POST /api/tourism/plan` valida IDs e calcula visitas e gastos.
5. `POST /api/tourism/route` consulta o perfil OSRM correto e retorna GeoJSON, distância e duração.
6. O navegador desenha o caminho real e numera as paradas.
7. `POST /api/chat` recebe a mensagem, o histórico limitado e o contexto do roteiro.

## Recomendação

Score heurístico: `0,8 * relevância + 0,2 * proximidade`. Na versão leve, a relevância vem da sobreposição de palavras normalizadas. Opcionalmente vem da similaridade de embeddings normalizados. Os pesos não foram calibrados com dados de usuários.

## Roteamento

Fonte: <https://routing.openstreetmap.de/about.html>. Protocolo: <https://project-osrm.org/docs/v26.5.0/http>. O perfil depende do grafo do servidor, não apenas do segmento `driving` da URL. O aplicativo seleciona `routed-foot`, `routed-bike` ou `routed-car`.

A rota preserva a ordem escolhida. Não há otimização automática de sequência. O serviço ajusta pontos à rede de caminhos; afastamentos acima de 100 m geram aviso. Falhas não produzem trajetos inventados. Transporte não é incluído nos gastos; tempo de deslocamento é mostrado separado e somado às visitas.

## Base turística

Dez lugares reais com referências de existência/história. Coordenadas aproximadas, durações e custos ilustrativos. Zero não confirma gratuidade. A data de consulta da fonte não equivale a verificação em campo. Não há sincronização de preços, horários ou disponibilidade.

Fontes por registro em `data/places.json`. Não há integração com Google Places; o link do Maps é navegação externa. Mapas OpenStreetMap e roteamento têm suas próprias políticas e limites.

## Assistente Cacau

Conhece a seleção atual e recupera até três sugestões da base. Adicionar um cartão é uma ação da pessoa. Orçamento mencionado pode ser aplicado por botão. Regras locais, API e adaptador treinado são modos distintos. A LLM não executa contas nem decide que uma região é segura.

## Segurança e limites

Não existe camada de criminalidade geográfica verificada. O aplicativo não classifica bairros ou ruas. Fonte de consulta: <https://www.ba.gov.br/ssp/informacoes-criminais-0>. Clima, marés, guias, reciclagem e recompensas são propostas futuras, não funcionalidades operacionais.

## Avaliação

`evaluation/run.py` mede Recall@3 e MRR@3 em seis consultas curadas próximas da base; não é um teste independente. A camada HTTP e os cálculos têm testes. O experimento de conversa tem dados e avaliação próprios em `ml/`.
