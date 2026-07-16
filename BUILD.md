# Build e instalação — PrintQuote by BMR

## 1. Gerar o ícone (só precisa rodar de novo se mudar o design)

```bash
python scripts/generate_icon.py
```

Gera os arquivos em `calc3d/ui/assets/` (`icon.ico` + PNGs).

## 2. Empacotar em .exe

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name "PrintQuote by BMR" --icon "calc3d/ui/assets/icon.ico" --add-data "calc3d/ui/assets;calc3d/ui/assets" main.py
```

Isso gera `dist/PrintQuote by BMR/` com o executável e todas as
dependências (PySide6, matplotlib etc.) — não precisa de Python instalado
na máquina de destino.

## 3. Instalar

```powershell
powershell -ExecutionPolicy Bypass -File installer\install.ps1
```

Instala em `%LOCALAPPDATA%\Programs\PrintQuote by BMR\` (não precisa de
administrador), cria atalhos no Menu Iniciar e na Área de Trabalho, e
registra o app em **Configurações > Aplicativos** com desinstalador.

## 4. Desinstalar

Pelo Windows: **Configurações > Aplicativos > PrintQuote by BMR > Desinstalar**.

Ou manualmente:
```powershell
powershell -ExecutionPolicy Bypass -File "%LOCALAPPDATA%\Programs\PrintQuote by BMR\uninstall.ps1"
```

Isso mantém seus dados (materiais, impressoras, histórico) em
`%LOCALAPPDATA%\BMR\PrintQuote by BMR\printquote.db`. Para apagar os dados
também, adicione `-PurgeData` no comando acima.

## Notas

- O build é feito com **PyInstaller** em modo pasta (`onedir`), não
  `onefile` — inicia mais rápido que um executável único.
- O instalador é um script PowerShell próprio (sem dependência de Inno
  Setup ou outra ferramenta externa) — só precisa do Windows.
- Sempre que o código mudar, repita os passos 2 e 3 para atualizar a
  instalação.
