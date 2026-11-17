# Colocar no GitHub e apresentar

## Repositório único

Nome sugerido: `portfolio-ia-amanda`. Esta pasta é um monorepositório: um servidor atende os dois projetos. Não mova apenas uma tela sem suas dependências de backend.

1. No GitHub, crie um repositório vazio com o nome escolhido. Não adicione arquivos iniciais por lá se for usar os comandos abaixo.
2. No terminal da pasta `portfolio-ia`, execute:

```powershell
git init
git add .
git status
git commit -m "Adiciona prototipos Ilheus AI e BuildBrief"
git branch -M main
```

3. Confirme em `git status`/`git diff --cached` que não há `.env`, chave, banco, `.venv`, `.venv-llm`, `.model-cache` ou dados privados.
4. Adicione a URL **real** do seu repositório:

```powershell
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

Substitua os dois nomes. A autenticação será a da sua própria conta; o pacote não contém token nem cria repositório automaticamente.

## Conteúdo que fortalece a candidatura

- README principal já incluído.
- Links para as duas documentações específicas.
- Capturas das interfaces em funcionamento.
- Vídeo curto de demonstração.
- Resultado da avaliação, com modo, amostra e limitações explícitos.
- Uma seção com suas decisões e o que você aprendeu ao revisar este código.

O pacote inclui um experimento de fine-tuning: confirme os manifestos e explique as limitações antes de citá-lo. Não houve publicação em Hugging Face ou competição Kaggle. Um embedding pré-treinado é diferente do adaptador de conversa ajustado neste projeto. Inclua dados, scripts, model card e métricas reais, sem os arquivos grandes do cache.

## Site

A apresentação está em `web/index.html` e é servida no endereço raiz do aplicativo. Ela inclui links locais para as duas demos. Antes de publicar, adicione seus links reais e revise sua apresentação.

GitHub Pages não executa o backend Python. Subir somente `web/` não torna as demos funcionais e os links absolutos precisariam de ajuste para um subdiretório. Para hoje, use vídeo e execução local; para hospedagem pública, prepare o backend conforme `ARQUITETURA.md` antes de expor o serviço.

Se quiser repositórios separados no futuro, extraia cada aplicativo junto de seus módulos, dados e testes; mantenha a página pessoal em um terceiro repositório com URLs reais das demos.


Modelos: publique o adaptador com as instruções do carregador, ou use ml/export_hf.py para produzir pesos fundidos. Preserve os créditos da base. O experimento inicial com respostas repetitivas também foi preservado, para documentar a análise de falhas.
