from odoo import models, fields


class TechstoreProducto(models.Model):
    _name = 'techstore.producto'
    _description = 'Producto TechStore'
    _order = 'name'

    name = fields.Char(string='Producto', required=True)
    codigo = fields.Char(string='Código')
    precio_unitario = fields.Float(string='Precio unitario', required=True)
    stock_disponible = fields.Integer(string='Stock disponible', default=10)
    activo = fields.Boolean(string='Activo', default=True)
