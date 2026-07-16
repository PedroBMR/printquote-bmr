# PrintQuote by BMR — versão web

Versão 100% estática (HTML + CSS + JS puro, sem build, sem backend) da
calculadora de custos e precificação para impressão 3D. Feita para rodar
direto no GitHub Pages — ou em qualquer hospedagem de arquivos estáticos.

## Rodar localmente

Não dá pra abrir `index.html` direto com duplo-clique (o navegador bloqueia
o `fetch`/import de módulos em `file://`) — sirva com um servidor simples:

```bash
cd web
python -m http.server 8080
```

Depois acesse `http://localhost:8080`.

## Publicar no GitHub Pages

1. Suba esta pasta (`web/`) pra um repositório no GitHub.
2. No repositório: **Settings > Pages**.
3. Em "Build and deployment", escolha **Deploy from a branch**.
4. Selecione a branch (ex: `main`) e a pasta `/web` (ou mova o conteúdo de
   `web/` pra raiz do repositório e selecione `/root`, se preferir raiz).
5. Salve — em alguns minutos o site fica disponível em
   `https://<seu-usuario>.github.io/<repositorio>/`.

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
| Motor de cálculo | `calc3d/core/calculator.py` | `web/js/core.js` (mesma lógica, portada) |
| Armazenamento | SQLite | localStorage do navegador |
| Exportar orçamento | PDF via `QPrinter` | Impressão do navegador (Ctrl+P / "Salvar como PDF") |
| Instalação | Instalador Windows (`.exe`) | Nenhuma — só abrir o link |

As fórmulas de custo e precificação são **idênticas** nas duas versões —
qualquer mudança nas regras de negócio deve ser replicada em
`calc3d/core/calculator.py` (desktop) **e** `web/js/core.js` (web).

## Estrutura

```
web/
  index.html       <- estrutura de todas as abas
  css/style.css    <- tema visual (glass, gradientes, animações)
  js/core.js       <- motor de cálculo puro (espelha o Python)
  js/store.js      <- persistência em localStorage + dados padrão
  js/app.js        <- UI: eventos, renderização, abas
  assets/          <- ícone/favicon (mesmos da versão desktop)
```
