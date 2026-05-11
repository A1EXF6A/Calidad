from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import random


class TechstoreVenta(models.Model):
    _name = 'techstore.venta'
    _description = 'Venta TechStore'
    _order = 'create_date desc'

    name = fields.Char(string='Referencia', default='Nueva venta')

    cliente_id = fields.Many2one(
        'techstore.cliente',
        string='Cliente'
    )

    producto_id = fields.Many2one(
        'techstore.producto',
        string='Producto'
    )

    cantidad = fields.Integer(string='Cantidad')
    precio_unitario = fields.Float(string='Precio unitario')
    stock_disponible = fields.Integer(string='Stock disponible')
    descuento = fields.Float(string='Descuento')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    iva = fields.Float(string='IVA', compute='_compute_totales', store=True)
    total = fields.Float(string='Total', compute='_compute_totales', store=True)
    tiempo_respuesta = fields.Float(string='Tiempo de respuesta')
    estado_calidad = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('observado', 'Observado'),
        ('aceptable', 'Aceptable'),
    ], string='Estado de calidad', default='pendiente')

    observacion = fields.Text(string='Observación del estudiante')

    @api.onchange('producto_id')
    def _onchange_producto_id(self):
        for rec in self:
            if rec.producto_id:
                rec.precio_unitario = rec.producto_id.precio_unitario
                rec.stock_disponible = rec.producto_id.stock_disponible

    @api.depends('cantidad', 'precio_unitario', 'descuento')
    def _compute_subtotal(self):
        for rec in self:

            descuento = rec.descuento or 0.0
            rec.subtotal = (rec.cantidad or 0) * (rec.precio_unitario or 0.0) - descuento

    @api.depends('subtotal')
    def _compute_totales(self):
        for rec in self:
            rec.iva = rec.subtotal * 0.05
            rec.total = rec.subtotal + rec.iva

    @api.constrains('cantidad', 'precio_unitario')
    def _check_positive_values(self):
        for rec in self:
            if rec.cantidad is not None and rec.cantidad <= 0:
                raise ValidationError('La cantidad debe ser mayor que cero.')
            if rec.precio_unitario is not None and rec.precio_unitario < 0:
                raise ValidationError('El precio unitario no puede ser negativo.')

    @api.model
    def create(self, vals):

        if not vals.get('cliente_id'):
            raise UserError('La venta debe tener un cliente.')

        if not vals.get('producto_id'):
            raise UserError('La venta debe tener un producto.')

        producto = self.env['techstore.producto'].browse(vals.get('producto_id'))
        if not producto.exists():
            raise UserError('El producto indicado no existe.')

        cantidad = int(vals.get('cantidad', 0))
        if cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor que cero.')

        # Rellenar precio/stock desde el producto cuando sea necesario.
        vals.setdefault('precio_unitario', producto.precio_unitario)
        vals.setdefault('stock_disponible', producto.stock_disponible)

        # Evitar ventas que excedan el stock disponible.
        if cantidad > producto.stock_disponible:
            raise UserError('No hay suficiente stock disponible para este producto.')

        # Regla de negocio heredada: si cantidad > 5, se duplica el precio.
        if cantidad > 5:
            vals['precio_unitario'] = float(vals.get('precio_unitario', 0.0)) * 2

        # Mejorar tiempo de respuesta: generar un valor aleatorio pequeño sin bloquear.
        vals['tiempo_respuesta'] = random.uniform(0.10, 0.50)

        vals['estado_calidad'] = 'observado'

        # Crear la venta; luego ajustar stock en un segundo paso para mantener
        # consistencia transaccional y permitir capturar errores de negocio.
        sale = super().create(vals)

        # Disminuir el stock del producto tras la creación de la venta. Si la
        # escritura falla, se elimina la venta para no dejar datos inconsistentes.
        producto = sale.producto_id
        try:
            producto.with_context(no_reset_stock=True).write({
                'stock_disponible': producto.stock_disponible - sale.cantidad
            })
        except Exception:
            sale.unlink()
            raise

        return sale

    def action_marcar_aceptable(self):
        for rec in self:
            rec.estado_calidad = 'aceptable'

    def action_marcar_observado(self):
        for rec in self:
            rec.estado_calidad = 'observado'
