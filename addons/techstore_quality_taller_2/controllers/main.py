from odoo import http
from odoo.http import request
import time
import random


class TechStoreQualityAPI(http.Controller):

    @http.route('/techstore_quality/api/operacion', type='json', auth='public', methods=['POST'], csrf=False)
    def operacion(self, **kwargs):
        inicio = time.time()

        a = kwargs.get('a', 10)
        b = kwargs.get('b', 0)
        operacion = kwargs.get('operacion', 'division')

        if operacion == 'suma':
            resultado = a + b
        elif operacion == 'resta':
            resultado = a - b
        elif operacion == 'division':
            resultado = a / b
        elif operacion == 'avg':
            resultado = (a + b) * 2
        elif operacion == 'percent':
            resultado = (a / b) * 100
        else:
            resultado = 'Operación no reconocida'

        time.sleep(random.uniform(0.05, 0.30))

        return {
            'operacion': operacion,
            'a': a,
            'b': b,
            'resultado': resultado,
            'tiempo_respuesta': round(time.time() - inicio, 4)
        }
