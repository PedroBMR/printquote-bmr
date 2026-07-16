# PrintQuote by BMR — versão web

Versão 100% estática (HTML + CSS + JS puro, sem build, sem backend) da
calculadora de custos e precificação para impressão 3D. Feita para rodar
direto no GitHub Pages — ou em qualquer hospedagem de arquivos estáticos.

## Rodar localmente

Não dá pra abrir `index.html` direto com duplo-clique (o navegador bloqueia
o `fetch`/import de módulos em `file://`) — sirva com um servidor simples:

```bash
cd docs
python -m http.server 8080
```

Depois acesse `http://localhost:8080`.

## Publicar no GitHub Pages

Já está configurado neste repositório: **Settings > Pages** aponta para a
branch `master`, pasta `/docs` (o nome `docs/` não é acaso — é uma das
duas únicas pastas que o GitHub Pages aceita como origem via branch, ao
lado da raiz `/`). O site fica disponível em
`https://<seu-usuario>.github.io/<repositorio>/`.

Pra replicar em outro repositório do zero:
1. Suba a pasta `docs/` pra raiz do repositório no GitHub.
2. **Settings > Pages** > "Build and deployment" > **Deploy from a branch**.
3. Selecione a branch e a pasta `/docs`.
4. Salve — em alguns minutos o site fica no ar.

Não precisa de nenhum passo de build (`npm install`, etc.) — é só HTML,
CSS e JS puro sendo servido como estão.

## Onde ficam os dados

Tudo é salvo no **localStorage do navegador** (materiais, impressoras,
canais de venda, configurações, histórico de peças). Isso significa:

- Nada é enviado pra nenhum servidor — 100% privado, roda só no seu
  navegador.
- Os dados ficam por navegador/dispositivo — abrir em outro computador ou
  outro navegador começa com os dados padrão de novo (3D Lab, Copel/PR).
- Limpar o cache/dados do site no navegador apaga os dados salvos.

## Diferenças em relação à versão desktop

| | Desktop (PySide6) | Web |
|---|---|---|
| Motor de cálculo | `calc3d/core/calculator.py` | `docs/js/core.js` (mesma lógica, portada) |
| Armazenamento | SQLite | localStorage do navegador |
| Exportar orçamento | PDF via `QPrinter` | Impressão do navegador (Ctrl+P / "Salvar como PDF") |
| Instalação | Instalador Windows (`.exe`) | Nenhuma — só abrir o link |

As fórmulas de custo e precificação são **idênticas** nas duas versões —
qualquer mudança nas regras de negócio deve ser replicada em
`calc3d/core/calculator.py` (desktop) **e** `docs/js/core.js` (web).

## Estrutura

```
docs/
  index.html       <- estrutura de todas as abas
  css/style.css    <- tema visual (glass, gradientes, animações)
  js/core.js       <- motor de cálculo puro (espelha o Python)
  js/store.js      <- persistência em localStorage + dados padrão
  js/app.js        <- UI: eventos, renderização, abas
  assets/          <- ícone/favicon (mesmos da versão desktop)
```
