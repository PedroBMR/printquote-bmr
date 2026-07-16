# Identidade visual — PrintQuote by BMR

Marca própria e independente da BMR (não é parte do NozzleNote — são
produtos irmãos, com identidades visuais separadas).

## Nome

**PrintQuote by BMR** — nome do produto exibido no título da janela, no
instalador e na tela "Aplicativos instalados" do Windows.

## Logo

Etiqueta de preço minimalista em gradiente violeta, com um furo circular
(estilo etiqueta física). Arquivos em `calc3d/ui/assets/`:

- `icon.ico` — ícone multi-resolução (16 a 256px), usado no `.exe`, atalhos
  e barra de tarefas
- `icon_512.png`, `icon_256.png`, `icon_128.png`, `icon_64.png`, `icon_32.png`
  — PNGs individuais para outros usos (site, redes sociais, documentação)

Gerados por `scripts/generate_icon.py` (Pillow) — rode o script novamente
se precisar regenerar em outra resolução ou ajustar as cores.

**Uso do logo:** manter a proporção original, não aplicar contorno,
sombra ou rotação. Funciona tanto sobre fundo escuro (`#0d1017`) quanto
sobre fundo claro/branco.

## Paleta de cores

Mesma paleta usada na interface (`calc3d/ui/theme.py`):

| Papel | Cor | Hex |
|---|---|---|
| Fundo geral | ⬛ | `#0d1017` |
| Superfície (cards) | ⬛ | `#141a26` |
| Superfície alternativa (inputs) | ⬛ | `#1a2233` |
| Borda sutil | ⬛ | `#2a3244` |
| Texto principal | ⬜ | `#f8fafc` |
| Texto secundário | ⬜ | `#94a3b8` |
| Texto apagado | ⬜ | `#64748b` |
| **Acento (marca)** | 🟣 | `#7c3aed` |
| Acento hover | 🟣 | `#8b5cf6` |
| Acento pressionado | 🟣 | `#6d28d9` |
| Acento claro (logo) | 🟣 | `#a78bfa` |
| Sucesso | 🟢 | `#22c55e` |
| Alerta | 🟡 | `#f59e0b` |
| Perigo | 🔴 | `#ef4444` |
| Info | 🔵 | `#0891b2` |

O gradiente do logo vai de `#a78bfa` (violet-400) a `#6d28d9` (violet-700).

## Tipografia

Segoe UI (nativa do Windows), com fallback para Inter/system-ui — mesma
fonte usada na interface do app.

## Onde a marca aparece

- Título da janela: `PrintQuote by BMR`
- Ícone do `.exe`, atalhos do Menu Iniciar/Desktop e barra de tarefas
- Rodapé dos orçamentos exportados em PDF
- Instalador e entrada em "Aplicativos instalados" do Windows
