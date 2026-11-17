"""Exemplos sintéticos autorais; não usam conversas privadas de usuários."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SYSTEM = "Você é um assistente dos projetos Cacau Trip e BuildBrief. Responda em português claro, com acentos. Use o contexto, explicite limitações e não invente dados."

# Perguntas de avaliação ficam separadas e não são inseridas no treinamento.
TRAIN = [
 ('tourism','Como escolher os lugares do meu roteiro?','No Cacau Trip, escolha um ponto no mapa, informe interesses e adicione os lugares que deseja visitar. Você controla a ordem das paradas.'),
 ('tourism','Quero passear por Ilhéus e gosto de literatura.','Busque literatura no Cacau Trip e veja os lugares cadastrados. A Casa de Cultura Jorge Amado é uma opção da base. Confirme funcionamento e preços antes da visita.'),
 ('tourism','Como calcular o caminho entre os pontos?','Adicione as paradas e clique em Traçar rota pelas ruas. Escolha a pé, carro ou bicicleta. O serviço OSRM calcula o caminho, a distância e o tempo estimado.'),
 ('tourism','Posso caminhar em linha reta entre os marcadores?','Não use a distância em linha reta como trajeto. Ela serve apenas para filtrar proximidade. A rota precisa seguir ruas e caminhos acessíveis.'),
 ('tourism','Os preços são confirmados?','Não. Os gastos iniciais do protótipo são simulações editáveis. Confira preços diretamente com os estabelecimentos; zero não confirma gratuidade.'),
 ('tourism','Qual é o bairro mais perigoso?','Não tenho dados locais verificados para classificar bairros. Uma rota não é uma avaliação de segurança. Consulte fontes oficiais e condições atuais.'),
 ('tourism','Qual a previsão de chuva hoje?','O protótipo não consulta clima em tempo real. Não posso informar a previsão atual. Consulte uma fonte meteorológica atualizada antes do passeio.'),
 ('tourism','Você sabe a maré de hoje?','Não há integração com marés no protótipo. Não vou inventar uma condição atual. Consulte uma fonte oficial atualizada.'),
 ('tourism','O chatbot já reservou meu passeio?','Não. O Cacau Trip não realiza reservas. Ele ajuda a escolher lugares e organizar um roteiro; qualquer contratação exige contato com o responsável.'),
 ('tourism','O roteiro inclui a passagem de transporte?','Não. O gasto de transporte não entra nas faixas simuladas por pessoa. Considere esse custo separadamente.'),
 ('tourism','Quero reduzir os gastos do passeio.','Revise as paradas e suas faixas de gastos. Você pode remover locais e ajustar os valores simulados. Confirme os preços reais antes de decidir.'),
 ('tourism','Posso levar duas pessoas no roteiro?','Sim. Informe o número de pessoas. O aplicativo soma o gasto simulado por pessoa e multiplica pelo grupo. Despesas compartilhadas não são modeladas.'),
 ('tourism','O que é o Assistente Cacau?','É o chatbot do Cacau Trip. Ele ajuda a entender as opções cadastradas e o roteiro escolhido. As contas e as rotas ficam em ferramentas separadas.'),
 ('tourism','Como faço para inverter duas paradas?','Use as setas de ordenação no roteiro. Depois trace a rota novamente: mudar a ordem invalida o caminho anterior.'),
 ('tourism','A rota considera trânsito agora?','Não. O serviço fornece uma estimativa sem trânsito em tempo real. Confirme as condições locais e reserve uma margem de tempo.'),
 ('tourism','A localização dos pontos foi medida em campo?','Não. As coordenadas da base inicial são aproximadas. Confirme a localização e a entrada de cada lugar antes de usar o roteiro.'),
 ('tourism','Como baixar o roteiro?','Clique em Baixar roteiro. O Markdown inclui as paradas, as simulações e, se calculada, a rota com distância e tempo de deslocamento.'),
 ('tourism','Quais lugares de comida estão na base?','A base inclui o Bar Vesúvio e o Espaço Bataclan entre as opções relacionadas à gastronomia e à cultura. Cardápios, preços e horários precisam de confirmação.'),
 ('tourism','Existem guias verificados no aplicativo?','Ainda não há catálogo operacional de guias. Essa é uma evolução planejada. Não existem contratações ou verificações de guias neste protótipo.'),
 ('tourism','Já posso trocar pontos de reciclagem?','Não. Recompensas e pontos de coleta são propostas de evolução, não serviços em operação. O protótipo atual se concentra em roteiro, mapa e conversa.'),
 ('tourism','Como a busca encontra lugares próximos?','O backend filtra a distância com Haversine e combina proximidade com interesses. Embeddings são opcionais. Essa distância não substitui a rota pelas ruas.'),
 ('tourism','Se a rota falhar, você inventa um caminho?','Não. Quando o serviço falha, o aplicativo informa o erro. Ele não substitui o caminho real por uma linha reta apresentada como rota.'),
 ('tourism','Como foi feito o mapa do Cacau Trip?','A interface usa Leaflet e dados do OpenStreetMap. O backend consulta OSRM para as rotas. Python calcula custos e valida as paradas.'),
 ('tourism','Qual é o valor exato da entrada hoje?','Não tenho preço atual confirmado. Os valores do protótipo são simulações. Consulte o estabelecimento e registre a fonte e a data da informação.'),
 ('brief','O que o BuildBrief faz?','O BuildBrief transforma uma ideia em um plano de software com requisitos, histórias, critérios de aceitação, entidades e tarefas. Também oferece chat, fluxograma e estimativas editáveis.'),
 ('brief','O que é um requisito funcional?','É uma capacidade que o sistema deve oferecer. No BuildBrief, requisitos possuem identificadores para conectar histórias e tarefas ao objetivo da funcionalidade.'),
 ('brief','Por que usar histórias de usuário?','Histórias relacionam o usuário, sua necessidade e o benefício esperado. Os critérios de aceitação tornam essa história verificável.'),
 ('brief','O que são critérios de aceitação?','São condições observáveis que indicam se uma história foi atendida. Inclua um exemplo de sucesso e um exemplo de entrada inválida ou falha.'),
 ('brief','Por onde começo a desenvolver?','Confirme o problema e o escopo antes de programar. Depois revise os requisitos, implemente as tarefas prioritárias e teste os critérios de aceitação.'),
 ('brief','Quais são as fases do planejamento?','O fluxo proposto começa na descoberta, passa pelas tarefas de implementação, integração e testes, e termina na documentação e validação da entrega.'),
 ('brief','Como o fluxograma é gerado?','O fluxograma usa as tarefas do plano e suas dependências sequenciais. Ele é desenhado em SVG e pode ser baixado. O ciclo de validação retorna aos ajustes quando necessário.'),
 ('brief','Os prazos são garantidos?','Não. São estimativas heurísticas editáveis, não promessas. Elas dependem do esforço, da complexidade, das horas por dia e da revisão do escopo.'),
 ('brief','Como ajustar a disponibilidade?','Altere Horas por dia e clique em Recalcular prazos. Uma capacidade menor tende a aumentar a quantidade de dias úteis estimados.'),
 ('brief','O cronograma considera os feriados?','Não. O cronograma considera segunda a sexta e não desconta feriados. Revise o calendário antes de assumir uma data de entrega.'),
 ('brief','Como mudar o esforço de uma tarefa?','Na tabela do cronograma, edite as horas mínimas e máximas da tarefa e recalcule. A faixa mínima não pode superar a máxima.'),
 ('brief','As tarefas são feitas em paralelo?','Nesta versão, a hipótese é uma pessoa e tarefas sequenciais. As dependências são propostas de planejamento, não relações descobertas automaticamente.'),
 ('brief','Retire os pagamentos online do projeto.','Esse pedido pode virar uma revisão. Confira o texto e salve uma nova versão para preservar o plano anterior. A conversa sozinha não altera requisitos.'),
 ('brief','A conversa apaga o plano anterior?','Não. Uma revisão confirmada cria uma nova versão no SQLite. O histórico permite consultar as versões anteriores.'),
 ('brief','Como exportar o planejamento?','Baixe o plano em Markdown, o cronograma em Markdown ou o fluxograma em SVG. Revise as estimativas antes de compartilhar.'),
 ('brief','A validação de JSON garante que o projeto está certo?','Não. Ela verifica o formato, os campos e as referências entre requisitos, histórias e tarefas. Correção técnica e completude precisam de revisão humana.'),
 ('brief','Qual é a diferença entre tarefa e requisito?','O requisito descreve o comportamento necessário. A tarefa descreve o trabalho para construí-lo. A referência ao requisito ajuda a manter rastreabilidade.'),
 ('brief','Como funciona o histórico?','Cada plano recebe um identificador. Uma revisão aponta para a versão anterior e é salva como um novo registro. Os dados ficam no computador local.'),
 ('brief','O sistema já programa a aplicação inteira?','Não. O BuildBrief prepara um plano revisável. A implementação do software continua exigindo decisões, código, testes e revisão.'),
 ('brief','Quais tecnologias compõem o BuildBrief?','O protótipo usa Python no backend, JavaScript na interface e SQLite para o histórico. O fluxograma é SVG. A integração generativa é configurável.'),
 ('brief','Como diminuir o escopo para uma primeira versão?','Priorize o fluxo principal, retire integrações opcionais e confirme os critérios de aceitação. Uma revisão do plano permite registrar o que ficou fora do escopo.'),
 ('brief','A IA consegue prever exatamente quantos dias vou levar?','Não. O cronograma é uma ferramenta de estimativa baseada em regras editáveis. Não é um modelo de previsão treinado com seu histórico de desenvolvimento.'),
 ('brief','Como confirmar uma mudança proposta no chat?','Use Preparar revisão no planejamento, revise o pedido e clique em Salvar nova versão. O botão do chat não salva mudanças automaticamente.'),
 ('brief','Como melhorar o planejamento depois da primeira versão?','Revise suposições, riscos e critérios com o interessado. Registre mudanças no histórico e atualize o esforço das tarefas com evidências do trabalho realizado.')
]
EVAL = [
 ('tourism','Dá para saber se esta rua é segura agora?','Não há dados locais verificados para classificar a segurança de ruas. Uma rota não garante segurança; consulte fontes oficiais e condições atuais.'),
 ('tourism','As faixas de reais mostradas nos cartões são os preços cobrados hoje?','Não. São simulações editáveis, sem confirmação de preço atual. Consulte o estabelecimento antes da visita.'),
 ('tourism','Depois de selecionar os pontos, como consigo um trajeto caminhando?','Escolha o modal a pé e clique em Traçar rota pelas ruas. O serviço retorna caminhos reais e tempo estimado; confirme os acessos locais.'),
 ('tourism','Vocês fecharam uma reserva quando cliquei em adicionar?','Não. Adicionar só altera o roteiro. O protótipo não realiza reservas nem contrata serviços.'),
 ('brief','A data final do cronograma pode ser tratada como compromisso?','Não. É uma estimativa heurística com suposições, não uma garantia. Revise esforço, disponibilidade e escopo.'),
 ('brief','Como documento que uma funcionalidade realmente ficou pronta?','Use critérios de aceitação observáveis, com exemplos de sucesso e falha. Depois teste a implementação contra esses critérios.'),
 ('brief','Onde vejo a versão antiga depois de pedir uma alteração?','Use o histórico local. Uma revisão confirmada gera outra versão sem sobrescrever a anterior.'),
 ('brief','Qual arquivo visual posso baixar para mostrar a sequência do trabalho?','Você pode baixar o fluxograma SVG. Ele mostra as fases, tarefas e o ciclo de validação do planejamento.')
]

def main():
    folder=ROOT/'data';folder.mkdir(parents=True,exist_ok=True)
    for split,items in [('train',TRAIN),('eval',EVAL)]:
        rows=[{'id':f'{split}-{i:03d}','project':project,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':question},{'role':'assistant','content':response}]} for i,(project,question,response) in enumerate(items)]
        content='\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n'
        (folder/(split+'.jsonl')).write_text(content,encoding='utf-8')
    assert not ({q for _,q,_ in TRAIN}&{q for _,q,_ in EVAL})
    print(f'Dataset sintético: {len(TRAIN)} treino, {len(EVAL)} avaliação. Sem perguntas idênticas entre as divisões.')

if __name__=='__main__':main()
