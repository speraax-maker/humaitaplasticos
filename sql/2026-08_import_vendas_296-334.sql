-- Base de vendas de agosto/2026 — pedidos 296 a 334.
-- Fonte: data/vendas_2026-08.tsv (planilha comercial).
-- Aplicado no projeto Supabase 'Humaitá Plásticos' em 24/08/2026.
--
-- O pedido 299 já existia no ERP (2026-0299, Brasil Tropical, 231 kg,
-- R$ 2.772,00) e confere com a planilha — por isso não é reimportado.
-- Os pedidos 300, 301 e 302 que já existiam no ERP são de outros
-- clientes (Acquaflex, Elias e Frigosuin) e foram renumerados para
-- 335, 336 e 337 para liberar a numeração da planilha.

BEGIN;

-- 1. Renumeração (do maior para o menor, para não colidir).
UPDATE pedidos SET numero='2026-0337', updated_at=now() WHERE ano=2026 AND numero='2026-0302';
UPDATE pedidos SET numero='2026-0336', updated_at=now() WHERE ano=2026 AND numero='2026-0301';
UPDATE pedidos SET numero='2026-0335', updated_at=now() WHERE ano=2026 AND numero='2026-0300';

-- 2. Cliente novo da planilha.
INSERT INTO clientes (empresa, prazo_pagamento) VALUES ('Daniel','30 dias')
  ON CONFLICT (empresa) DO NOTHING;

-- 3. Produtos novos (itens codificados da Mais Q Limpeza).
--    Os códigos 809, 1437 e 3095 já existiam com outro rótulo e foram
--    reaproveitados em vez de duplicados.
INSERT INTO produtos (sku, nome, peso_unitario, unidade_medida) VALUES
  ('100L-P4-PRETO-2KG-COD-2356', '100L P4 Preto - 2KG - Cód. 2356', 2.00, 'kg'),
  ('100L-P6-PRETO-2-3KG-COD-2357', '100L P6 Preto - 2,3KG - Cód. 2357', 2.30, 'kg'),
  ('100L-P7-PRETO-2-7KG-COD-2358', '100L P7 Preto - 2,7KG - Cód. 2358', 2.70, 'kg'),
  ('100L-P7-PRETO-C-100-UNI-COD-4242', '100L P7 Preto - C/ 100 uni. - Cód.4242', 4.50, 'kg'),
  ('100L-P9-PRETO-3-6KG-COD-3637', '100L P9 Preto - 3,6KG - Cód. 3637', 3.60, 'kg'),
  ('200L-P6-PRETO-C-100UNI-COD-4287', '200L P6 Preto - C/ 100uni - Cód.4287', 5.53, 'kg'),
  ('200L-P8-PRETO-C-100UNI-COD-4288', '200L P8 Preto - C/ 100uni - Cód.4288', 6.53, 'kg')
  ON CONFLICT (sku) DO NOTHING;

-- 4. Pedidos e itens (38 pedidos, 137 itens).
WITH dados(ped, dt, cliente, produto, qtd, peso, preco) AS (VALUES
(296,'2026-08-04','Caebitex','75x120 REF Canela - Sanfonado',10,100.00,12.00),
(297,'2026-08-04','Um Metro','40x58 REF Canela - 250 uni',28,210.00,12.00),
(298,'2026-08-04','Celso','100L BL REF Preto',10,50.00,9.00),
(298,'2026-08-04','Celso','200L REF Preto',10,50.00,9.00),
(298,'2026-08-04','Celso','100L REF Preto',25,125.00,9.00),
(298,'2026-08-04','Celso','60L REF Preto',25,125.00,9.00),
(298,'2026-08-04','Celso','80L REF Preto',10,50.00,9.00),
(298,'2026-08-04','Celso','100L Fino Preto - 100 uni',10,51.00,9.50),
(298,'2026-08-04','Celso','60L Fino Preto - 100 uni',30,96.00,9.50),
(300,'2026-08-05','Maria','20L Fino Preto - 100 uni',5,7.50,9.50),
(300,'2026-08-05','Maria','40L Fino Preto - 100 uni',5,12.50,9.50),
(300,'2026-08-05','Maria','60L Fino Preto - 100 uni',5,16.50,9.50),
(300,'2026-08-05','Maria','100L BL Fino Preto - 100 uni',5,25.00,9.50),
(300,'2026-08-05','Maria','100L Fino Preto - 100 uni',5,25.00,9.50),
(300,'2026-08-05','Maria','200L REF Preto',5,25.00,9.50),
(301,'2026-08-05','Mais Q Limpeza','300L Preto - 4KG - Cód. 809',49,196.00,9.30),
(301,'2026-08-05','Mais Q Limpeza','300L Preto - 3KG - Cód. 1437',15,45.00,9.30),
(301,'2026-08-05','Mais Q Limpeza','100L P4 Preto - 2KG - Cód. 2356',30,60.00,9.30),
(301,'2026-08-05','Mais Q Limpeza','100L P6 Preto - 2,3KG - Cód. 2357',31,71.30,9.30),
(301,'2026-08-05','Mais Q Limpeza','100L P7 Preto - C/ 100 uni. - Cód.4242',50,225.00,9.30),
(301,'2026-08-05','Mais Q Limpeza','100L Preto - 3,2KG - Cód. 3095',30,96.00,9.30),
(301,'2026-08-05','Mais Q Limpeza','100L P9 Preto - 3,6KG - Cód. 3637',20,72.00,9.30),
(301,'2026-08-05','Mais Q Limpeza','200L P6 Preto - C/ 100uni - Cód.4287',19,105.00,9.30),
(301,'2026-08-05','Mais Q Limpeza','200L P8 Preto - C/ 100uni - Cód.4288',15,97.90,9.30),
(301,'2026-08-05','Mais Q Limpeza','100L P7 Preto - 2,7KG - Cód. 2358',25,67.50,9.30),
(302,'2026-08-06','Marcos','200L REF Preto',3,15.00,9.00),
(302,'2026-08-06','Marcos','100L BL REF Preto',15,75.00,9.00),
(302,'2026-08-06','Marcos','100L BL Fino Preto - 100 uni',18,90.00,9.00),
(302,'2026-08-06','Marcos','60L Fino Preto - 100 uni',10,30.00,9.00),
(302,'2026-08-06','Marcos','40L Fino Preto - 100 uni',5,12.50,9.00),
(302,'2026-08-06','Marcos','20L Fino Preto - 100 uni',15,24.00,9.00),
(303,'2026-08-06','Innova Limp','100L P5 Preto - 80 uni',27,108.00,9.50),
(303,'2026-08-06','Innova Limp','30L P2 Preto - 80 uni',25,40.00,9.50),
(303,'2026-08-06','Innova Limp','200L P8 Preto - 80 uni',8,51.20,9.50),
(303,'2026-08-06','Innova Limp','40L P2.5 Preto - 80 uni',20,40.00,9.50),
(304,'2026-08-06','Celso','100L REF Preto',20,100.00,9.00),
(304,'2026-08-06','Celso','80L REF Preto',5,25.00,9.00),
(304,'2026-08-06','Celso','60L REF Preto',25,125.00,9.00),
(304,'2026-08-06','Celso','40L REF Preto',8,40.00,9.00),
(304,'2026-08-06','Celso','100L Fino Preto - 100 uni',14,71.00,9.50),
(304,'2026-08-06','Celso','60L Fino Preto - 100 uni',20,57.00,9.50),
(304,'2026-08-06','Celso','40L Fino Preto - 100 uni',20,42.00,9.50),
(305,'2026-08-06','Senhora dos Nós','Bobina 60cm REF Canela',2,79.00,12.00),
(306,'2026-08-06','Manoel','100L REF Preto',30,150.00,9.50),
(306,'2026-08-06','Manoel','60L REF Preto',8,40.00,9.50),
(306,'2026-08-06','Manoel','40L REF Preto',2,10.00,9.50),
(307,'2026-08-07','Skimpack','100L BL REF Preto',50,250.00,9.00),
(307,'2026-08-07','Skimpack','60L REF Preto',30,150.00,9.00),
(307,'2026-08-07','Skimpack','40L REF Preto',5,25.00,9.00),
(307,'2026-08-07','Skimpack','200L REF Preto',10,50.00,9.00),
(307,'2026-08-07','Skimpack','100L BL Fino Preto - 100 uni',10,50.00,9.50),
(307,'2026-08-07','Skimpack','60L Fino Preto - 100 uni',40,120.00,9.50),
(307,'2026-08-07','Skimpack','40L Fino Preto - 100 uni',20,40.00,9.50),
(307,'2026-08-07','Skimpack','20L Fino Preto - 100 uni',10,13.00,9.50),
(308,'2026-08-10','Marcos','100L BL REF Preto',50,250.00,9.00),
(309,'2026-08-11','Lauro','70x100 REF Canela',11,110.00,12.00),
(310,'2026-08-11','Sky Master','95x150 REF Canela',32,320.00,13.00),
(310,'2026-08-11','Sky Master','95x180 REF Canela',30,300.00,13.00),
(310,'2026-08-11','Sky Master','95x105 REF Canela',20,200.00,13.00),
(311,'2026-08-12','Maria','100L BL Fino Preto - 100 uni',10,50.00,9.50),
(311,'2026-08-12','Maria','60L Fino Preto - 100 uni',10,33.00,9.50),
(311,'2026-08-12','Maria','40L Fino Preto - 100 uni',10,25.00,9.50),
(311,'2026-08-12','Maria','20L Fino Preto - 100 uni',10,15.00,9.50),
(311,'2026-08-12','Maria','100L BL REF Preto',10,50.00,9.50),
(312,'2026-08-12','Arena Buck','60L REF Preto',1,5.00,12.00),
(312,'2026-08-12','Arena Buck','100L BL REF Preto',2,10.00,12.00),
(313,'2026-08-13','Posto BR','100L BL REF Preto',2,10.00,12.00),
(314,'2026-08-13','Arican','100L BL REF Preto',6,30.00,10.00),
(314,'2026-08-13','Arican','200L REF Preto',6,30.00,10.00),
(314,'2026-08-13','Arican','20L REF Preto',6,30.00,10.00),
(314,'2026-08-13','Arican','60L REF Preto',6,30.00,10.00),
(315,'2026-08-13','DellMac','90x150 REF Preto',10,100.00,10.00),
(316,'2026-08-13','Innova Limp','60L P3 Preto - 80 uni',50,120.00,9.50),
(316,'2026-08-13','Innova Limp','100L P4 Preto - 80 uni',59,188.80,9.50),
(316,'2026-08-13','Innova Limp','20L P1.5 Preto - 80 uni',45,54.00,9.50),
(316,'2026-08-13','Innova Limp','100L P5 Preto - 80 uni',10,40.00,9.50),
(317,'2026-08-13','Mazinho','100L REF Preto',20,100.00,9.50),
(317,'2026-08-13','Mazinho','60L REF Preto',20,100.00,9.50),
(317,'2026-08-13','Mazinho','40L REF Preto',10,50.00,9.50),
(317,'2026-08-13','Mazinho','20L REF Preto',5,25.00,9.50),
(317,'2026-08-13','Mazinho','200L REF Preto',2,10.00,9.50),
(318,'2026-08-13','Um Metro','35x55 REF Canela',5,10.00,13.00),
(318,'2026-08-13','Um Metro','40x58 REF Canela - 250 uni',38,285.00,12.00),
(318,'2026-08-13','Um Metro','61x82 REF Canela',4,24.00,12.00),
(319,'2026-08-14','ACG Comercial','20L REF Preto',1,5.00,9.00),
(319,'2026-08-14','ACG Comercial','40L REF Preto',1,5.00,9.00),
(319,'2026-08-14','ACG Comercial','60L REF Preto',3,15.00,9.00),
(319,'2026-08-14','ACG Comercial','100L BL REF Preto',2,10.00,9.00),
(320,'2026-08-14','Rough Collie','20L REF Preto',10,50.00,9.00),
(320,'2026-08-14','Rough Collie','60L REF Preto',3,15.00,9.00),
(320,'2026-08-14','Rough Collie','100L BL REF Preto',1,5.00,9.00),
(321,'2026-08-14','Maria','100L Fino Preto - 100 uni',10,60.00,9.50),
(322,'2026-08-14','Anderson','Bobina 60cm REF Canela',4,288.00,11.00),
(323,'2026-08-18','Celso','100L BL REF Preto',5,25.00,9.00),
(323,'2026-08-18','Celso','200L REF Preto',10,50.00,9.00),
(323,'2026-08-18','Celso','100L REF Preto',40,200.00,9.00),
(323,'2026-08-18','Celso','60L REF Preto',10,50.00,9.00),
(323,'2026-08-18','Celso','100L Fino Preto - 100 uni',12,62.00,9.50),
(323,'2026-08-18','Celso','60L Fino Preto - 100 uni',25,80.00,9.50),
(323,'2026-08-18','Celso','20L Fino Preto - 100 uni',25,38.00,9.50),
(324,'2026-08-18','Innova Limp','100L P4 Preto - 80 uni',40,128.00,9.50),
(324,'2026-08-18','Innova Limp','100L P5 Preto - 80 uni',20,80.00,9.50),
(324,'2026-08-18','Innova Limp','100L P7 Preto - 80 uni',20,112.00,9.50),
(324,'2026-08-18','Innova Limp','40L P2.5 Preto - 80 uni',20,40.00,9.50),
(325,'2026-08-18','Brasil Tropical','70x140 REF Canela',5,49.00,12.00),
(325,'2026-08-18','Brasil Tropical','70x80 REF Canela',5,50.00,12.00),
(325,'2026-08-18','Brasil Tropical','80x95 REF Canela',6,56.00,12.00),
(326,'2026-08-18','Jair','60L REF Preto',20,100.00,9.50),
(326,'2026-08-18','Jair','100L REF Preto',10,50.00,9.50),
(326,'2026-08-18','Jair','40L REF Preto',5,25.00,9.50),
(327,'2026-08-19','Caebitex','300L REF Canela',5,50.00,12.00),
(327,'2026-08-19','Caebitex','35x55 Fino Canela',45,225.00,12.00),
(328,'2026-08-19','Steel Fire','50x60 REF Canela',20,100.00,12.00),
(329,'2026-08-20','Priscila','100L BL REF Preto',25,125.00,10.00),
(329,'2026-08-20','Priscila','60L REF Preto',20,100.00,10.00),
(330,'2026-08-20','Acquaflex','65x100 REF Canela',815,96.00,11.50),
(330,'2026-08-20','Acquaflex','75x125 REF Canela',400,59.00,11.50),
(330,'2026-08-20','Acquaflex','80x125 REF Canela',378,71.00,11.50),
(330,'2026-08-20','Acquaflex','85x125 REF Canela',244,49.00,11.50),
(331,'2026-08-20','Um Metro','40x58 REF Canela - 250 uni',26,195.00,12.00),
(332,'2026-08-21','Daniel','200L REF Preto',10,10.00,47.50),
(332,'2026-08-21','Daniel','100L Fino Preto - 100 uni',60,60.00,50.00),
(332,'2026-08-21','Daniel','60L Fino Preto - 100 uni',60,60.00,30.00),
(332,'2026-08-21','Daniel','40L Fino Preto - 100 uni',60,60.00,25.00),
(333,'2026-08-21','Celso','100L Fino Preto - 100 uni',10,51.00,9.50),
(333,'2026-08-21','Celso','60L Fino Preto - 100 uni',20,62.00,9.50),
(333,'2026-08-21','Celso','40L Fino Preto - 100 uni',15,33.00,9.50),
(333,'2026-08-21','Celso','200L REF Preto',10,50.00,9.00),
(333,'2026-08-21','Celso','100L BL REF Preto',10,50.00,9.00),
(333,'2026-08-21','Celso','100L REF Preto',20,100.00,9.00),
(333,'2026-08-21','Celso','80L REF Preto',8,40.00,9.00),
(333,'2026-08-21','Celso','60L REF Preto',15,75.00,9.00),
(333,'2026-08-21','Celso','40L REF Preto',5,25.00,9.00),
(333,'2026-08-21','Celso','20L REF Preto',5,25.00,9.00),
(334,'2026-08-21','Innova Limp','100L P4 Preto - 80 uni',10,32.00,9.50),
(334,'2026-08-21','Innova Limp','100L P5 Preto - 80 uni',10,40.00,9.50),
(334,'2026-08-21','Innova Limp','60L P5 Preto - 80 uni',20,80.00,9.50)
), novos AS (
  INSERT INTO pedidos (numero, ano, cliente_id, data_pedido, total, status)
  SELECT '2026-0'||d.ped, 2026, c.id, d.dt::date, sum(d.peso*d.preco), 'confirmado'
    FROM dados d JOIN clientes c ON c.empresa = d.cliente
   GROUP BY d.ped, d.dt, c.id
  RETURNING id, numero
)
INSERT INTO pedido_itens (pedido_id, produto_id, sku, quantidade, peso_kg, preco_kg)
SELECT n.id, p.id, p.sku, d.qtd, d.peso, d.preco
  FROM dados d
  JOIN novos n ON n.numero = '2026-0'||d.ped
  JOIN produtos p ON p.nome = d.produto;

COMMIT;
