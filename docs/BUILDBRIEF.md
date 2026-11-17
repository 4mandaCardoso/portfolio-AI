# BuildBrief · Documentação do projeto

## Problema e solução

Ideias vagas dificultam começar um software. O BuildBrief estrutura contexto, explicita suposições e gera artefatos revisáveis. A pessoa pode comparar versões e exportar um plano.

## Modos

| Modo | Comportamento |
| --- | --- |
| demo | Template determinístico. Reconhece palavras de cinco domínios e produz um esqueleto de cadastro, consulta e atualização. Não avalia viabilidade nem interpreta qualquer pedido |
| llm | Envia contexto, exemplo de estrutura e plano anterior ao provedor configurado; valida JSON, campos, IDs, critérios e referências |

No demo, exclusão explícita de pagamentos é reconhecida e registrada. Demais revisões entram como pergunta pendente. A restrição textual é preservada, não integralmente verificada. Em modo LLM, uma resposta estruturalmente válida ainda pode desrespeitar uma regra de negócio; cabe revisão humana e avaliação específica.

## API

`POST /api/briefs/generate`:

```json
{"idea":"Sistema de reservas para pousadas","audience":"Recepcionistas","deadline":"1 semana","technologies":"Python e JavaScript","constraints":"Sem pagamentos online","use_llm":false}
```

Resposta contém `id`, `parent_id`, `created_at`, `inputs`, `plan`, `mode`, `revision`.

Para revisar, use a mesma rota:

```json
{"parent_id":1,"revision":"retire pagamentos online","use_llm":false}
```

O backend carrega a entrada e o plano da versão pai. Alterações no formulário da tela só valem para **um novo plano**, não para a revisão de uma versão. Revisões podem criar ramificações do histórico e não sobrescrevem o pai.

- `GET /api/briefs`: últimas 50 versões, mais recentes primeiro.
- `GET /api/brief?id=1`: versão completa.
- `GET /api/brief/export?id=1`: Markdown da versão, com entrada e modo.

## Validação

- Campos de entrada com tamanho limitado.
- Listas obrigatórias e itens não vazios.
- IDs únicos dentro de requisitos, histórias e tarefas.
- Cada história/tarefa referencia requisito existente.
- Cada história possui critérios de aceitação.
- Entidades possuem lista de campos.
- Corpo HTTP limitado a 64 KB.
- Uma geração de plano por vez no servidor local.

Resultados de modelo são renderizados com `textContent`, sem executar HTML gerado. Isso não torna o conteúdo tecnicamente confiável; reduz a superfície de execução no navegador.

## Persistência

SQLite em `runtime/briefs.sqlite3`. Tabela `versions(id,parent_id,created_at,payload)`. Cada revisão é uma nova linha. Consultas usam parâmetros SQL. A conexão é curta e a escrita é transacional. Não há login, sincronização ou separação entre usuários; usar apenas localmente.

## Avaliação

Testes automatizados cobrem preservação do pai, referências quebradas, critérios vazios, domínio, exportação e integração HTTP em memória. O script de avaliação valida cinco planos demonstrativos. Nenhum deles mede qualidade de um modelo generativo real.

Para avaliar LLM: prepare ideias independentes, estabeleça requisitos esperados, registre versão/modelo/prompt e avalie cobertura, contradições, rastreabilidade e respeito a restrições. Meça erros de JSON, tempo e custo. Não registre chaves ou conteúdo confidencial.

## Evoluções

- Comparação visual entre versões.
- Revisor independente com critérios e exemplos fixos.
- Exportação para ferramenta de tarefas mediante autorização explícita.
- Recuperação de padrões de arquitetura de uma base técnica curada.
- Autenticação, retenção e exclusão de dados para uso multiusuário.


## Fluxograma e prazos da versão 2

POST /api/brief/schedule recebe record_id e options (start_date, hours_day, complexity, overrides). Retorna fases, dependências sequenciais propostas, horas mínimas/máximas e datas em cenários de esforço. O cálculo está em scheduling.py; o SVG em web/planning.js. Não há previsão treinada de produtividade.

## Chat e experimento de fine-tuning

POST /api/chat recebe project=brief, mensagem, histórico limitado, record_id e opções de cronograma. O servidor carrega a versão autorizada localmente e calcula o cronograma, sem confiar em requisitos inventados enviados pelo navegador. O modo de regras explica o plano; o modo API usa o provedor; o modo LoRA usa o adaptador experimental treinado no projeto. A geração do plano JSON não utiliza esse modelo compacto, que foi ajustado somente para conversa.

Revisões preparadas pelo chat precisam de confirmação em Salvar nova versão. Não há alteração silenciosa de requisitos. Mais detalhes em NOVIDADES_V2.md e ../ml/README.md.
