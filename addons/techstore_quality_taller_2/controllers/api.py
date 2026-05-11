from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
import json


def _extract_request_data(kwargs):
    """Return parsed dict from kwargs or request body.

    Handles three cases:
    - kwargs passed directly by Odoo routing
    - JSON-RPC body with top-level 'params'
    - plain JSON body
    """
    if kwargs:
        return dict(kwargs)
    # Fallback: try to read raw request body (compatible with this Odoo env)
    try:
        raw = request.httprequest.get_data(as_text=True) or ''
        if raw:
            parsed = json.loads(raw)
        else:
            parsed = {}
    except Exception:
        parsed = {}
    if isinstance(parsed, dict) and 'params' in parsed and isinstance(parsed['params'], dict):
        return parsed['params']
    return parsed or {}


class TechstoreAPI(http.Controller):
    @http.route('/techstore/api/clients', type='json', auth='none', methods=['POST'], cors='*')
    def create_client(self, **kwargs):
        """
        Endpoint para crear clientes desde sistemas externos.
        Añadimos validaciones en la API para devolver errores legibles
        y evitar que la base de datos devuelva un error genérico de constraint
        (por ejemplo: columna "name" no nula).
        """
        # Detectar datos tanto si llegan por kwargs directo como si Odoo
        # envolver la petición en JSON-RPC (entonces los parámetros están en
        # `request.jsonrequest['params']` o en `request.jsonrequest`).
        data = _extract_request_data(kwargs)

        # Validación mínima requerida por el modelo
        name = data.get('name')
        if not name:
            return {'success': False, 'error': 'El campo "name" es obligatorio para crear un cliente.'}
        try:
            vals = {
                'name': name,
                'cedula': data.get('cedula'),
                'email': data.get('email'),
                'telefono': data.get('telefono'),
                'activo': data.get('activo', True),
            }
            # Usamos sudo() para permitir llamadas externas en entornos de testing;
            # en producción deberías securizar el endpoint o usar auth apropiado.
            client = request.env['techstore.cliente'].sudo().create(vals)
            return {'success': True, 'id': client.id}
        except (ValidationError, UserError) as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/techstore/api/clients', type='http', auth='none', methods=['GET'], cors='*')
    def list_clients(self, **kwargs):
        clients = request.env['techstore.cliente'].sudo().search([])
        result = []
        for c in clients:
            result.append({
                'id': c.id,
                'name': c.name,
                'cedula': c.cedula,
                'email': c.email,
                'telefono': c.telefono,
                'activo': c.activo,
            })
        body = json.dumps(result, default=str)
        return request.make_response(body, [('Content-Type', 'application/json')])

    @http.route('/techstore/api/products', type='json', auth='none', methods=['POST'], cors='*')
    def create_product(self, **kwargs):
        """
        Endpoint para crear productos. Validaciones previas evitan errores
        de tipo y reglas de negocio (precio/stock no negativos).
        """
        data = _extract_request_data(kwargs)

        name = data.get('name')
        if not name:
            return {'success': False, 'error': 'El campo "name" es obligatorio para crear un producto.'}
        precio = data.get('precio_unitario', 0.0)
        stock = data.get('stock_disponible', 0)
        try:
            precio = float(precio)
        except Exception:
            return {'success': False, 'error': 'El campo "precio_unitario" debe ser numérico.'}
        try:
            stock = int(stock)
        except Exception:
            return {'success': False, 'error': 'El campo "stock_disponible" debe ser entero.'}
        if precio < 0:
            return {'success': False, 'error': 'El precio unitario no puede ser negativo.'}
        if stock < 0:
            return {'success': False, 'error': 'El stock disponible no puede ser negativo.'}
        try:
            vals = {
                'name': name,
                'codigo': data.get('codigo'),
                'precio_unitario': precio,
                'stock_disponible': stock,
                'activo': data.get('activo', True),
            }
            product = request.env['techstore.producto'].sudo().create(vals)
            return {'success': True, 'id': product.id}
        except (ValidationError, UserError) as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/techstore/api/products', type='http', auth='none', methods=['GET'], cors='*')
    def list_products(self, **kwargs):
        prods = request.env['techstore.producto'].sudo().search([])
        result = []
        for p in prods:
            result.append({
                'id': p.id,
                'name': p.name,
                'codigo': p.codigo,
                'precio_unitario': p.precio_unitario,
                'stock_disponible': p.stock_disponible,
                'activo': p.activo,
            })
        body = json.dumps(result, default=str)
        return request.make_response(body, [('Content-Type', 'application/json')])

    @http.route('/techstore/api/sales', type='json', auth='none', methods=['POST'], cors='*')
    def create_sale(self, **kwargs):
        """
        Endpoint para crear ventas. Validamos IDs y tipos en la API para
        dar mensajes de error más amigables y evitar errores SQL/NotNull.
        """
        data = _extract_request_data(kwargs)

        cliente_id = data.get('cliente_id')
        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad')
        if not cliente_id:
            return {'success': False, 'error': 'cliente_id es obligatorio.'}
        if not producto_id:
            return {'success': False, 'error': 'producto_id es obligatorio.'}
        try:
            cantidad = int(cantidad)
        except Exception:
            return {'success': False, 'error': 'cantidad debe ser un entero mayor que cero.'}
        if cantidad <= 0:
            return {'success': False, 'error': 'cantidad debe ser mayor que cero.'}
        try:
            vals = {
                'cliente_id': cliente_id,
                'producto_id': producto_id,
                'cantidad': cantidad,
                'descuento': data.get('descuento', 0.0),
            }
            sale = request.env['techstore.venta'].sudo().create(vals)
            # `invalidate_cache` asegura que los campos computados se recalcule
            # y es compatible con la API de recordsets en esta versión de Odoo.
            try:
                sale.invalidate_cache()
            except Exception:
                pass
            return {
                'success': True,
                'id': sale.id,
                'subtotal': sale.subtotal,
                'iva': sale.iva,
                'total': sale.total,
                'tiempo_respuesta': sale.tiempo_respuesta,
            }
        except (ValidationError, UserError) as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/techstore/api/sales', type='http', auth='none', methods=['GET'], cors='*')
    def list_sales(self, **kwargs):
        sales = request.env['techstore.venta'].sudo().search([])
        result = []
        for s in sales:
            result.append({
                'id': s.id,
                'name': s.name,
                'cliente_id': s.cliente_id.id if s.cliente_id else None,
                'producto_id': s.producto_id.id if s.producto_id else None,
                'cantidad': s.cantidad,
                'precio_unitario': s.precio_unitario,
                'subtotal': s.subtotal,
                'iva': s.iva,
                'total': s.total,
                'tiempo_respuesta': s.tiempo_respuesta,
            })
        body = json.dumps(result, default=str)
        return request.make_response(body, [('Content-Type', 'application/json')])
