select date
from report_pos_order
WHERE date >= date_trunc('month', current_date - INTERVAL '6 months')
group by date;


SELECT *
FROM product_product as pp
         INNER join product_template AS pt ON pp.product_tmpl_id = pt.id
WHERE pt.default_code = '220103';

-- ESTA QUERY FUNCIONA
SELECT id, sq.mes, sq.total
FROM product_product AS pp
         INNER JOIN (SELECT product_id, to_char(pol.create_date, 'TMMonth YYYY') as mes, sum(pol.qty) as total
                     -- average of pol.qty
                     FROM pos_order_line as pol
                     WHERE create_date >= date_trunc('month', current_date - INTERVAL '6 months')
                     GROUP BY mes, product_id) AS sq ON pp.id = sq.product_id
WHERE pp.default_code = '220103';

SELECT id, sq.mes, sq.total
FROM product_product AS pp
         INNER JOIN (SELECT product_id, to_char(pol.create_date, 'TMMonth YYYY') as mes, sum(pol.qty) as total
                     -- average of pol.qty
                     FROM pos_order_line as pol
                     WHERE create_date >= date_trunc('month', current_date - INTERVAL '6 months')
                     GROUP BY mes, product_id) AS sq ON pp.id = sq.product_id
WHERE pp.default_code = '220103';

-- group by pol.create_date, product_id
-- order by mes;

SELECT (SELECT SUM(qty) FROM pos_order_line) / (SELECT COUNT(*) FROM pos_order_line) AS avg_qty;

SELECT *
FROM product_template;


SELECT *
FROM stock_bids_product_resume;