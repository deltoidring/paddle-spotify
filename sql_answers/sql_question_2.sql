WITH ITEMS AS (
  SELECT
    P.PRODUCT_CATEGORY_NAME,
    OI.PRICE,
    OI.ORDER_ITEM_ID,
    WEEK(O.ORDER_PURCHASE_TIMESTAMP) AS ORDER_WEEK
  FROM
    ORDER_ITEMS OI
    LEFT JOIN ORDERS O ON O.ORDER_ID = OI.ORDER_ID
    LEFT JOIN PRODUCTS P ON P.PRODUCT_ID = OI.PRODUCT_ID
  WHERE
    YEAR(O.ORDER_PURCHASE_TIMESTAMP) = 2017
    AND MONTH(O.ORDER_PURCHASE_TIMESTAMP) = 11
),
TOP_CATEGORIES AS (
  SELECT
    PRODUCT_CATEGORY_NAME,
    COUNT(ORDER_ITEM_ID) AS ITEMS_SOLD
  FROM
    ITEMS
  GROUP BY
    PRODUCT_CATEGORY_NAME
  ORDER BY
    ITEMS_SOLD DESC
  LIMIT
    3
), WEEKLY_GMV AS (
  SELECT
    PRODUCT_CATEGORY_NAME,
    ORDER_WEEK,
    SUM(PRICE) AS GMV
  FROM
    ITEMS
  WHERE
    PRODUCT_CATEGORY_NAME IN (
      SELECT
        PRODUCT_CATEGORY_NAME
      FROM
        TOP_CATEGORIES
    )
  GROUP BY
    PRODUCT_CATEGORY_NAME,
    ORDER_WEEK
)
SELECT
  *,
  GMV - LAG (GMV) OVER (
    PARTITION BY PRODUCT_CATEGORY_NAME
    ORDER BY
      ORDER_WEEK ASC
  ) AS GMV_GROWTH_ABS,
  ROUND(
    (
      GMV - LAG (GMV) OVER (
        PARTITION BY PRODUCT_CATEGORY_NAME
        ORDER BY
          ORDER_WEEK ASC
      )
    ) / LAG(GMV) OVER (
      PARTITION BY PRODUCT_CATEGORY_NAME
      ORDER BY
        ORDER_WEEK ASC
    ) * 100,
    2
  ) AS GMV_GROWTH_PERCENTAGE,
  SUM(GMV) OVER (
    PARTITION BY PRODUCT_CATEGORY_NAME
    ORDER BY
      ORDER_WEEK ASC ROWS BETWEEN UNBOUNDED PRECEDING
      AND CURRENT ROW
  ) AS TOTAL_SOLD_GMV
FROM
  WEEKLY_GMV
ORDER BY
  ORDER_WEEK,
  PRODUCT_CATEGORY_NAME