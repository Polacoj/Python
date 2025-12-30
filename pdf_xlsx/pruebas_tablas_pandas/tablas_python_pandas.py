import pandas as pd
from datetime import datetime

# Crear DataFrame de ejemplo
data = {
    'Fecha': [datetime(2024, 1, 15), datetime(2024, 1, 16)],
    'Producto': ['Laptop', 'Mouse'],
    'Cantidad': [10, 50],
    'Precio Unitario': [1200.50, 25.99],
    'Total': [12005.00, 1299.50],
    'Descuento': [0.15, 0.05]
}

df = pd.DataFrame(data)

# Crear writer de Excel
with pd.ExcelWriter('formato_pandas.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Ventas', index=False)
    
    # Obtener el workbook y worksheet
    workbook = writer.book
    worksheet = writer.sheets['Ventas']
    
    # Definir formatos
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#366092',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    currency_format = workbook.add_format({
        'num_format': '"$"#,##0.00',
        'align': 'right'
    })
    
    percent_format = workbook.add_format({
        'num_format': '0.00%',
        'align': 'right'
    })
    
    date_format = workbook.add_format({
        'num_format': 'dd/mm/yyyy',
        'align': 'center'
    })
    
    # Aplicar formatos a columnas
    worksheet.set_column('A:A', 12, date_format)  # Fecha
    worksheet.set_column('B:B', 15)  # Producto
    worksheet.set_column('C:C', 10)  # Cantidad
    worksheet.set_column('D:D', 15, currency_format)  # Precio
    worksheet.set_column('E:E', 15, currency_format)  # Total
    worksheet.set_column('F:F', 12, percent_format)  # Descuento
    
    # Formato de encabezados
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    
    # Autoajustar ancho de columnas
    for i, col in enumerate(df.columns):
        column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
        worksheet.set_column(i, i, column_width)
    
    # Formato condicional
    red_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    green_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    
    # Resaltar cantidades mayores a 20
    worksheet.conditional_format('C2:C100', {
        'type': 'cell',
        'criteria': '>',
        'value': 20,
        'format': green_format
    })