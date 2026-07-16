# PrintQuote by BMR

Calculadora de custos e precificação para impressão 3D, com identidade
visual própria da marca BMR. Duas versões, mesmo motor de cálculo:

- **Desktop** (este README) — app PySide6 standalone com instalador Windows.
- **Web** — versão estática (HTML/CSS/JS puro, sem backend), publicada via
  GitHub Pages a partir da pasta `docs/`. Veja [docs/README.md](docs/README.md).

## Como rodar (a partir do código)

```bash
pip install -r requirements.txt
python main.py
```

O banco SQLite é criado automaticamente em
`%LOCALAPPDATA%\BMR\PrintQuote by BMR\printquote.db` na primeira execução,
já populado com materiais, impressoras (Ender 3 S1, Bambu Lab A1 + AMS Lite,
P1S) e canais de venda padrão — tudo editável pela interface.

## Gerar o instalador Windows

Veja [BUILD.md](BUILD.md) para empacotar o app em um `.exe` standalone e
gerar o instalador (atalhos no Menu Iniciar/Desktop, entrada em
"Aplicativos instalados", desinstalador).

## Identidade visual

Veja [BRANDING.md](BRANDING.md) para paleta de cores, ícone e diretrizes
de uso da marca.

## Arquitetura (para uma futura integração com outros apps BMR)

```
calc3d/
  core/            <- MOTOR DE CÁLCULO (Python puro, zero UI, zero SQL)
    models.py      <- dataclasses: Material, PrinterProfile, PieceInput,
                        CostBreakdown, PricingScenario, PricingResult...
    calculator.py   <- funções puras: compute_breakdown(), compute_pricing()

  data/            <- CAMADA DE DADOS (SQLite)
    database.py    <- schema + conexão
    repository.py  <- CRUD (materials, printers, sale_channels,
                        app_settings, parts_history)
    defaults.py    <- seed inicial (materiais/impressoras/canais padrão)

  ui/              <- INTERFACE STANDALONE (PySide6)
    main_window.py + tab_*.py
```

### Integração futura com o NozzleNote

- **`core/`** é a parte que deve ser importada diretamente no NozzleNote
  (`from calc3d.core.calculator import compute_pricing`). Não tem nenhuma
  dependência de PySide6 nem de SQLite — só recebe `PieceInput` +
  `GlobalSettings` e devolve um `PricingResult`. Pode virar uma nova aba lá
  reaproveitando 100% dessa lógica.
- **`data/`** usa o mesmo padrão de SQLite que o NozzleNote já usa. Se o
  NozzleNote apontar para o mesmo arquivo de banco (ou você migrar as
  tabelas `materials`/`printers`/`parts_history` para o banco dele), os
  dados podem ser compartilhados entre os dois apps sem conversão.
- **`ui/`** é descartável na integração — o NozzleNote vai construir sua
  própria tela usando os mesmos `core`/`data`, então essa camada não precisa
  ser tocada nem reaproveitada.

### Fórmulas principais do motor de cálculo

- `custo_material = peso_g * (1 + %desperdício) * preço_por_grama`
- `custo_energia = (potência_W / 1000) * horas_impressão * tarifa_kWh`
- `depreciação_hora = valor_pago / vida_útil_horas`
- `custo_base = material + energia + depreciação + manutenção + mão_de_obra`
- `custo_ajustado_falha = custo_base / (1 - taxa_falha)` — divisão, não
  multiplicação, é a forma tecnicamente correta de diluir perdas
- `custo_total = custo_ajustado_falha + overhead + embalagem + frete_absorvido`
- **Cost-plus:** `preço = custo_total * (1 + markup)`
- **Margem sobre preço:** `preço = (custo_total + taxa_fixa) / (1 - margem - taxas% - imposto%)`
  (resolve o preço já considerando que taxas de marketplace/gateway/imposto
  incidem sobre o preço final, não sobre o custo)
- **Comparação com concorrente:** dado um preço informado, calcula o lucro
  líquido real e a margem real àquele preço.

## Biblioteca de materiais

Cadastre filamentos/resinas uma vez na aba **Materiais** (nome, tipo,
preço por kg ou por litro) e depois só selecione da lista suspensa ao
montar uma peça na aba **Calculadora** — sem precisar redigitar preços.
