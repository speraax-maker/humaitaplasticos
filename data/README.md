# Base de vendas

`vendas_2026-08.tsv` — planilha comercial de agosto/2026 (pedidos 296 a 334),
uma linha por item. Colunas: `pedido`, `data`, `cliente`, `qtd`, `produto`,
`peso_total` (kg), `preco_kg` (R$/kg), `peso_unitario` (kg), `total` (R$).

Em todas as 139 linhas vale `total = peso_total × preco_kg`.

O arquivo é a fonte de `sql/2026-08_import_vendas_296-334.sql`, já aplicado no
Supabase em 24/08/2026:

- pedido **299** já existia no ERP e confere com a planilha — não foi reimportado;
- pedidos **300, 301 e 302** do ERP eram de outros clientes (Acquaflex, Elias e
  Frigosuin) e foram renumerados para **335, 336 e 337**;
- os demais 38 pedidos (137 itens) foram importados — 2026 fica com 337 pedidos,
  numerados de 0001 a 0337, sem lacunas e sem repetições.

Ponto em aberto: na linha do pedido **332** a planilha traz `Data = 20/08/2026`
mas as colunas `Dia/Mês` dizem `21/8`. Foi importado como **21/08/2026**.
