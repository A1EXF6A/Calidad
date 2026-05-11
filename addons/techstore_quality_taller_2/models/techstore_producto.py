from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TechstoreProducto(models.Model):
    # Clase que representa productos. Aquí se agregaron:
    # - Restricción SQL para que `codigo` sea único.
    # - Constraint en Python para evitar valores negativos en precio y stock.
    # Estas defensas en dos capas (API/modelo/DB) ayudan a mantener integridad desde
    # diversas fuentes de creación/actualización (UI, XML, API externa).
    _name = 'techstore.producto'
    _description = 'Producto TechStore'
    _order = 'name'

    name = fields.Char(string='Producto', required=True)
    codigo = fields.Char(string='Código')
    precio_unitario = fields.Float(string='Precio unitario', required=True)
    stock_disponible = fields.Integer(string='Stock disponible', default=10)
    activo = fields.Boolean(string='Activo', default=True)

    # Unicidad a nivel BD para evitar duplicados en código.
    _sql_constraints = [
        ('codigo_unique', 'unique(codigo)', 'El código del producto debe ser único.'),
    ]

    @api.constrains('precio_unitario', 'stock_disponible')
    def _check_non_negative(self):
        """
        Evita que se guarden precios o stock negativos.
        - Se lanza `ValidationError` para que Odoo muestre un mensaje claro al usuario
          y las APIs puedan capturar el error.
        """
        for rec in self:
            if rec.precio_unitario is not None and rec.precio_unitario < 0:
                raise ValidationError('El precio unitario no puede ser negativo.')
            if rec.stock_disponible is not None and rec.stock_disponible < 0:
                raise ValidationError('El stock disponible no puede ser negativo.')
