from odoo import models, fields


class TechstoreCliente(models.Model):
    _name = 'techstore.cliente'
    _description = 'Cliente TechStore'
    _order = 'name'

    name = fields.Char(string='Nombre del cliente', required=True)
    cedula = fields.Char(string='Cédula/RUC')
    email = fields.Char(string='Correo')
    telefono = fields.Char(string='Teléfono')
    activo = fields.Boolean(string='Activo', default=True)
