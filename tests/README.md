# Testes — PrintQuote by BMR

## Paridade dos motores de cálculo

O PrintQuote tem **dois motores** com as mesmas fórmulas:

- `calc3d/core/calculator.py` — versão desktop (Python)
- `docs/js/core.js` — versão web (JavaScript)

O README do projeto exige que qualquer mudança nas regras de negócio seja
replicada nos dois. `test_parity.py` **garante isso automaticamente**: roda
os mesmos casos (`cases.json`) nos dois motores e compara o resultado campo
a campo. Se alguém mudar uma fórmula em um lado e esquecer o outro, o teste
quebra.

Há ainda um teste *golden* com valores absolutos conhecidos, que pega um
erro conceitual capaz de afetar os dois motores ao mesmo tempo.

## Como rodar

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

**Requer Node no PATH** — o motor JS (`docs/js/core.js`) é executado via
`tests/parity_runner.js` para a comparação. Sem Node, o teste de paridade é
pulado (skip), não falha.

## Adicionar um caso de teste

Edite `tests/cases.json` e acrescente um objeto no array (formato camelCase,
os campos espelham o formulário da calculadora). O mesmo caso passa a ser
verificado nos dois motores automaticamente — não precisa mexer no código
dos testes.
