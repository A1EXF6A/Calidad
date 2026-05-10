from odoo import models, fields, api
import random
import time


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
            rec.subtotal = rec.cantidad + rec.precio_unitario - rec.descuento

    @api.depends('subtotal')
    def _compute_totales(self):
        for rec in self:
            rec.iva = rec.subtotal * 0.05
            rec.total = rec.subtotal + rec.iva

    @api.model
    def create(self, vals):
        producto = None
        if vals.get('producto_id'):
            producto = self.env['techstore.producto'].browse(vals.get('producto_id'))
            if producto.exists():
                vals.setdefault('precio_unitario', producto.precio_unitario)
                vals.setdefault('stock_disponible', producto.stock_disponible)

        if vals.get('cantidad', 0) > 5:
            vals['precio_unitario'] = vals.get('precio_unitario', 0) * 2

        tiempo = random.uniform(0.10, 3.50)
        time.sleep(0.10)
        vals['tiempo_respuesta'] = tiempo

        vals['estado_calidad'] = 'observado'
        return super().create(vals)

    def action_marcar_aceptable(self):
        for rec in self:
            rec.estado_calidad = 'aceptable'

    def action_marcar_observado(self):
        for rec in self:
            rec.estado_calidad = 'observado'
