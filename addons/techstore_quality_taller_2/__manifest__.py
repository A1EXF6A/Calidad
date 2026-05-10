{
    'name': 'TechStore Quality - Taller Realista con Fallas',
    'version': '1.0',
    'summary': 'Escenario realista con clientes, productos y ventas con fallas intencionales',
    'description': 'Módulo para taller de ACS, métricas y aseguramiento estadístico con errores intencionales.',
    'author': 'Taller ACS',
    'category': 'Education',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/techstore_demo_data.xml',
        'views/techstore_cliente_views.xml',
        'views/techstore_producto_views.xml',
        'views/techstore_venta_views.xml',
        'views/z_techstore_menu.xml',
    ],
    'installable': True,
    'application': True,
}
