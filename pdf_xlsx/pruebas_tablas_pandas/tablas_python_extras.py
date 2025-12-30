def aplicar_formato_celda(celda, formato_dict):
    """Aplica un diccionario de formatos a una celda"""
    for atributo, valor in formato_dict.items():
        if hasattr(celda, atributo):
            setattr(celda, atributo, valor)

def crear_formato_moneda(color_fondo=None):
    """Crea formato de moneda con fondo opcional"""
    formato = {
        'number_format': '"$"#,##0.00',
        'alignment': Alignment(horizontal='right')
    }
    
    if color_fondo:
        formato['fill'] = PatternFill(
            start_color=color_fondo,
            end_color=color_fondo,
            fill_type='solid'
        )
    
    return formato

def formatear_rango(ws, rango, formato_dict):
    """Aplica formato a un rango de celdas"""
    for row in ws[rango]:
        for cell in row:
            aplicar_formato_celda(cell, formato_dict)


formatos_numericos = {
    'entero': '0',
    'entero_con_separador': '#,##0',
    'decimal_2': '0.00',
    'decimal_2_con_separador': '#,##0.00',
    'moneda': '"$"#,##0.00',
    'moneda_euro': '[$€] #,##0.00',
    'porcentaje': '0%',
    'porcentaje_2_decimales': '0.00%',
    'fecha_corta': 'dd/mm/yyyy',
    'fecha_larga': 'dddd, dd "de" mmmm "de" yyyy',
    'hora': 'hh:mm:ss',
    'fecha_hora': 'dd/mm/yyyy hh:mm:ss',
    'texto': '@',  # Fuerza formato de texto
    'cientifico': '0.00E+00'
}

