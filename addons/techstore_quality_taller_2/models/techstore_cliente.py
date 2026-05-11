from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TechstoreCliente(models.Model):
    _name = 'techstore.cliente'
    _description = 'Cliente TechStore'
    _order = 'name'
    # Clase que representa clientes. Se añadieron restricciones y validaciones
    # para garantizar integridad de datos y evitar duplicados.
    name = fields.Char(string='Nombre del cliente', required=True)
    cedula = fields.Char(string='Cédula/RUC')
    email = fields.Char(string='Correo')
    telefono = fields.Char(string='Teléfono')
    activo = fields.Boolean(string='Activo', default=True)

    # Restricciones SQL para evitar duplicados a nivel de base de datos.
    # Se añadieron porque el requerimiento pide unicidad en correo, cédula y teléfono.
    _sql_constraints = [
        ('email_unique', 'unique(email)', 'El correo debe ser único.'),
        ('cedula_unique', 'unique(cedula)', 'La cédula/RUC debe ser única.'),
        ('telefono_unique', 'unique(telefono)', 'El teléfono debe ser único.'),
    ]

    @api.constrains('telefono')
    def _check_telefono_length(self):
        """
        Validación adicional de negocio: la longitud del teléfono debe ser exactamente 10 dígitos.
        Esta validación evita insertar valores inválidos desde la UI o APIs externas y
        proporciona mensajes de error claros antes de llegar a restricciones SQL.
        """
        for rec in self:
            if rec.telefono:
                digits = ''.join(ch for ch in rec.telefono if ch.isdigit())
                if len(digits) != 10:
                    raise ValidationError('El teléfono debe contener exactamente 10 dígitos.')
