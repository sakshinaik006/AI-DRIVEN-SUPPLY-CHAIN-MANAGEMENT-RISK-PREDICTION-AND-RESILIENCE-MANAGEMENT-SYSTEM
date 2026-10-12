# Data and Mapping Assumptions

## DataCo Electronics

- The DataCo SMART Supply Chain dataset is historical source data.
- Rows were filtered to `Category Name == "Electronics"`.
- The order and shipping dates were shifted by one consistent offset so the earliest Electronics order starts on 2025-04-01.
- Only rows with shifted order dates from 2025-04-01 through 2025-10-31 were retained.
- The current processed file contains 811 Electronics order rows; 2,345 rows were outside the selected date window and excluded.
- These are date-shifted historical records, not real transactions from 2025.
- Raw and processed datasets are kept locally and excluded from Git. The preprocessing script is committed.

## Synthetic Network

- Supplier, plant, warehouse, route, product, and component master data are synthetic and do not represent real companies or facilities.
- Any links between suppliers, components, plants, warehouses, routes, and products are simulation assumptions.
- DataCo product/order records may be mapped to synthetic product and warehouse IDs using documented category and location rules. These mappings do not establish a real-world business relationship.
- News or weather signals are linked to simulated entities only through documented location/entity matching rules.

## Limitations

- DataCo does not provide a complete supplier-to-plant-to-warehouse network.
- Date shifting changes the calendar dates but does not make the historical data representative of real 2025 operations.
- Model results should be presented as a pipeline demonstration, not evidence of real-world predictive accuracy.
- Agmarknet is excluded because agricultural-market prices are not a defensible direct proxy for smartphone-component prices.