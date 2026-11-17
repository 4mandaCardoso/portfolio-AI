# Publicar os protótipos no GitHub e no Render

O pacote tem dois modos de execução. `iniciar.py` atende à demonstração local. Para Render, use **backend.webapp:app**, com FastAPI/Uvicorn e sessão separada por navegador. Todos os projetos continuam sendo protótipos.

## 1. Preparar a pasta

1. Baixe o ZIP atualizado e use **Extrair tudo**.
2. Abra a pasta `portfolio-ia` no VS Code.
3. Confirme que `README.md`, `render.yaml`, `requirements-render.txt`, `backend/` e `web/` aparecem nessa pasta.
4. Não envie apenas o ZIP ou somente `web/` para o GitHub: o Render precisa dos arquivos extraídos.

## 2. Criar o repositório no GitHub

1. Entre em https://github.com/new.
2. Escolha um nome, por exemplo **portfolio-ia-amanda**.
3. Escolha Public se quiser mostrar o código aos recrutadores, ou Private se preferir controlar o acesso.
4. Nesta criação, deixe desmarcadas as opções de gerar README, licença e `.gitignore`, pois os arquivos já estão no pacote.
5. Clique em Create repository.

Instale Git se ainda não tiver e abra o terminal **dentro de portfolio-ia**. Execute um comando por linha:

```powershell
git init
git add .
git status
```

Confira o que será enviado. Não devem aparecer `.env`, `.venv`, `.venv-llm`, `.venv-render`, `.model-cache` ou `runtime`. O `.gitignore` já exclui esses caminhos. Os adaptadores pequenos, os exemplos sintéticos e os relatórios podem ser versionados, respeitando os créditos e licenças das bases.

Depois:

```powershell
git commit -m "Adiciona prototipos Cacau Trip e BuildBrief"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/portfolio-ia-amanda.git
git push -u origin main
```

Substitua `SEU_USUARIO` e o nome do repositório pelos seus. Autorize o acesso à sua conta quando o Git solicitar. Sua senha normal do GitHub não deve ser usada como senha de Git por HTTPS; prefira o gerenciador de credenciais/login do navegador.

Se o Git pedir nome/e-mail para o commit, configure nessa pasta, com seus dados reais:

```powershell
git config user.name "Amanda Cardoso Lopes"
git config user.email "SEU_EMAIL_DO_GITHUB"
```

Repita `git commit` e `git push` após configurar. Se já existir `origin`, confira `git remote -v`; não adicione o mesmo remoto de novo.

### Alternativa sem terminal

Use GitHub Desktop: **File → Add local repository**; se a pasta ainda não for um repositório, crie um nela, faça o commit inicial e use **Publish repository**. Revise a opção de repositório privado antes de publicar.

## 3. Hospedar os aplicativos completos no Render

1. Acesse https://dashboard.render.com e entre na sua conta.
2. Escolha **New → Web Service**.
3. Conecte o GitHub e selecione o repositório.
4. Preencha:

| Campo | Valor |
| --- | --- |
| Name | `amanda-portfolio-prototipos` ou um nome disponível |
| Language / Runtime | Python |
| Branch | `main` |
| Root Directory | Vazio, se `backend/` e `render.yaml` estão na raiz do repositório |
| Build Command | `pip install -r requirements-render.txt` |
| Start Command | `uvicorn backend.webapp:app --host 0.0.0.0 --port $PORT --workers 1` |
| Health Check Path | `/api/health` |
| Instance Type | Free para a primeira demonstração leve |

Se você enviou a pasta `portfolio-ia` inteira **dentro** do repositório, em vez de enviar seu conteúdo na raiz, preencha Root Directory com `portfolio-ia`.

### Variáveis de ambiente

Antes de criar o serviço, abra Environment e adicione:

| Chave | Valor |
| --- | --- |
| `SESSION_SECRET` | Um segredo aleatório longo, exclusivo deste serviço |
| `RECOMMENDER` | `keyword` |
| `ENABLE_REMOTE_LLM` | `false` |
| `ENABLE_TRAINED_LLM` | `false` |

Para gerar um segredo no seu terminal:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copie o resultado para `SESSION_SECRET` **apenas no painel do Render**. Não cole no código, README ou GitHub. Não use a frase do exemplo como segredo. Essa variável assina as sessões para que um navegador não consulte o histórico de outro.

Clique em **Create Web Service** e acompanhe os logs até o serviço ficar Live. Abra a URL fornecida pelo Render. Não há um endereço fixo predefinido pelo pacote.

Teste:

1. A página inicial mostra a foto inteira, com identificação abaixo e aviso de protótipo.
2. `/api/health` responde com `status: ok`.
3. O Cacau Trip busca lugares e traça rotas ao clicar.
4. O BuildBrief gera plano, cronograma e fluxograma.
5. Os chats funcionam no modo **Regras locais**.

### Alternativa com Blueprint

O arquivo `render.yaml` já configura o serviço. No Render, escolha **New → Blueprint**, conecte o repositório e revise a configuração antes de confirmar. O Blueprint gera `SESSION_SECRET` automaticamente. A criação e a escolha do plano são feitas na sua conta; não foram executadas por este pacote.

## 4. Usar uma LLM pela API no Render

O serviço leve não instala PyTorch nem carrega o modelo treinado. Para ativar um provedor externo compatível, configure no painel do Render:

```dotenv
ENABLE_REMOTE_LLM=true
LLM_BASE_URL=https://ENDERECO-REAL-DO-PROVEDOR/v1
LLM_MODEL=IDENTIFICADOR-REAL-DO-MODELO
LLM_API_KEY=SUA-CHAVE-REAL
```

Salve e faça o redeploy. A opção via API ficará disponível no chat. As chamadas podem gerar cobrança e o serviço recebe o conteúdo enviado. O protótipo tem limites de demonstração: 30 solicitações POST por sessão/hora e 120 no total por hora, mantidos em memória para uma instância. Isso não substitui autenticação e controle de uso de produção.

Não coloque a chave no JavaScript do navegador. Não envie o arquivo `.env` para o GitHub.

## 5. E a LLM treinada localmente?

Ela continua no pacote com os adaptadores e os relatórios. A execução observada usou um modelo de aproximadamente 0,5 bilhão de parâmetros em float32; exige bem mais memória que a versão web leve. Não recomendo habilitar esse modo na instância Free.

Para demonstrar o modelo gratuitamente no seu computador, use `INICIAR_IA_TREINADA.bat`. O site pode apresentar os resultados e um vídeo dessa demonstração. Para inferência online do adaptador, será necessário dimensionar um serviço com memória adequada ou exportá-lo para uma infraestrutura de inferência compatível, avaliando os custos antes. Os resultados ainda são experimentais e apresentam imprecisões.

## 6. Histórico no plano Free

O banco SQLite da hospedagem fica em armazenamento temporário por padrão. Reinícios e novos deploys podem apagar o histórico. A instância gratuita também pode suspender por inatividade, causando uma espera ao abrir novamente.

Para persistência, escolha um serviço com disco persistente e configure `APP_DATA_DIR` para o caminho desse disco, ou migre para um banco gerenciado. Discos persistentes não são oferecidos em Web Services Free. Não escolha um plano pago sem revisar o preço e a necessidade.

## 7. Atualizar depois

Após editar arquivos:

```powershell
git add .
git commit -m "Atualiza os prototipos do portfolio"
git push
```

Com auto-deploy habilitado, o Render cria uma nova versão a partir do commit. Caso contrário, use Manual Deploy no painel. O site privado publicado anteriormente é uma hospedagem separada: um push ao seu GitHub não altera automaticamente aquela prévia.

## Fontes oficiais

- GitHub: https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github
- Render Web Services: https://render.com/docs/web-services
- FastAPI no Render: https://render.com/docs/deploy-fastapi
- Limites Free: https://render.com/docs/free
- Discos persistentes: https://render.com/docs/disks
