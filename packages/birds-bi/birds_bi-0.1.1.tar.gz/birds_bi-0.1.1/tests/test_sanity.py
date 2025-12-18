from birds_bi import Repository, Component

foja = Repository(r"C:\repos\FOJA groep\Birds-FOJA-BC2ADLS")


fact_sales_order = Component(repo=foja, category="fact", component="salesorder")
for table_definition in fact_sales_order.table_definitions:
    print(table_definition.table_identifier)
    print(table_definition.schema)
    for column in table_definition.columns:
        print(column.column_name)