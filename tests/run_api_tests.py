#!/usr/bin/env python3
"""
Script de pruebas para los endpoints del módulo TechStore.
Genera un informe detallado en `tests/report.txt` y escribe resultados por consola.

Uso:
    python tests/run_api_tests.py

Nota: el servidor Odoo debe estar corriendo en `http://localhost:8069` o ajustar
la variable `BASE_URL` abajo.
"""
import requests
import time
import traceback
import os
import random

BASE_URL = os.environ.get('TECHSTORE_BASE_URL', 'http://localhost:8069')

REPORT_PATH = os.path.join(os.path.dirname(__file__), 'report.txt')


def now():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def post_json(path, payload):
    url = BASE_URL + path
    t0 = time.time()
    try:
        r = requests.post(url, json=payload, timeout=10)
        dt = time.time() - t0
        try:
            data = r.json()
        except Exception:
            data = {'raw_text': r.text}
        return {'ok': True, 'status_code': r.status_code, 'time': dt, 'response': data}
    except Exception as e:
        dt = time.time() - t0
        return {'ok': False, 'time': dt, 'error': str(e), 'trace': traceback.format_exc()}


def get_json(path):
    url = BASE_URL + path
    t0 = time.time()
    try:
        r = requests.get(url, timeout=10)
        dt = time.time() - t0
        try:
            data = r.json()
        except Exception:
            data = {'raw_text': r.text}
        return {'ok': True, 'status_code': r.status_code, 'time': dt, 'response': data}
    except Exception as e:
        dt = time.time() - t0
        return {'ok': False, 'time': dt, 'error': str(e), 'trace': traceback.format_exc()}


def write_report(entries):
    lines = []
    lines.append('TechStore API Test Report')
    lines.append('Generated: %s' % now())
    lines.append('Base URL: %s' % BASE_URL)
    lines.append('')
    total_time = 0.0
    total_tests = 0
    passed = 0
    failed = 0
    provocado = 0
    for e in entries:
        total_tests += 1
        lines.append('---')
        lines.append('Test: %s' % e.get('name'))
        lines.append('Path: %s' % e.get('path'))
        lines.append('Payload: %s' % repr(e.get('payload')))
        if e.get('result') is None:
            lines.append('Result: NO RESPONSE')
            failed += 1
            continue
        r = e['result']
        if r.get('ok'):
            lines.append('HTTP status: %s' % r.get('status_code'))
            lines.append('Time (s): %.4f' % r.get('time'))
            total_time += r.get('time', 0)
            lines.append('Response: %s' % repr(r.get('response')))
            # considerar passed/failed en base al contenido lógico de la respuesta
            try:
                resp = r.get('response')
                # soportar wrapper JSON-RPC
                if isinstance(resp, dict) and 'result' in resp and isinstance(resp['result'], dict):
                    ok = resp['result'].get('success', False)
                elif isinstance(resp, dict) and 'success' in resp:
                    ok = resp.get('success', False)
                else:
                    # GET requests devuelven listas -> considerarlas passed
                    ok = True
            except Exception:
                ok = False
            if ok:
                passed += 1
            else:
                failed += 1
            # detectar si fue un test provocado (se esperaba error)
            if '(error esperado)' in e.get('name', ''):
                provocado += 1
        else:
            lines.append('ERROR: %s' % r.get('error'))
            lines.append('Trace: %s' % r.get('trace'))
            failed += 1
            if '(error esperado)' in e.get('name', ''):
                provocado += 1
    lines.append('')
    # Resumen
    avg_time = (total_time / max(1, total_tests))
    lines.append('')
    lines.append('**Resumen de pruebas**')
    lines.append('Total tests: %d' % total_tests)
    lines.append('Pasados: %d' % passed)
    lines.append('Fallados: %d' % failed)
    lines.append('Provocados (errores esperados): %d' % provocado)
    lines.append('Tiempo total requests (s): %.4f' % total_time)
    lines.append('Tiempo promedio por request (s): %.4f' % avg_time)

    lines.append('')
    lines.append('Total requests time (s): %.4f' % total_time)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('\n'.join(lines))


def run_tests():
    entries = []

    # Generar sufijo único por ejecución para evitar colisiones con datos previos
    suffix = str(int(time.time() * 1000)) + str(random.randint(0, 999))
    email_juan = f"juan{suffix}@test.com"
    codigo_teclado = f"TK-{suffix}"
    codigo_neg = f"TK-NEG-{suffix}"
    email_ana = f"ana{suffix}@test.com"
    # Generar cedulas y teléfonos únicos (10 dígitos para teléfono)
    cedula_juan = str(1000000000 + int(suffix[-6:]))
    cedula_no_name = str(2000000000 + int(suffix[-6:]))
    cedula_ana = str(3000000000 + int(suffix[-6:]))
    telefono_juan = '09' + suffix[-8:].rjust(8, '0')[:8]
    telefono_no_name = '09' + str(int(suffix[-8:]) + 1).rjust(8, '0')[:8]

    # 1) Crear cliente válido
    payload = {'name': 'Juan Perez', 'cedula': cedula_juan, 'email': email_juan, 'telefono': telefono_juan}
    res = post_json('/techstore/api/clients', payload)
    entries.append({'name': 'Crear cliente válido', 'path': '/techstore/api/clients', 'payload': payload, 'result': res})
    client_id = None
    if res.get('ok') and isinstance(res.get('response'), dict):
        # the JSON-RPC wrapper for type='json' returns a dict with 'result' sometimes
        resp = res.get('response')
        if 'result' in resp and isinstance(resp['result'], dict):
            client_id = resp['result'].get('id')
        else:
            client_id = resp.get('id') or resp.get('result')

    # 2) Intentar crear cliente sin nombre (debe fallar)
    payload = {'cedula': cedula_no_name, 'email': f'no_name{suffix}@test.com', 'telefono': telefono_no_name}
    res = post_json('/techstore/api/clients', payload)
    entries.append({'name': 'Crear cliente sin name (error esperado)', 'path': '/techstore/api/clients', 'payload': payload, 'result': res})

    # 3) Crear producto válido
    payload = {'name': 'Teclado', 'codigo': codigo_teclado, 'precio_unitario': 25.5, 'stock_disponible': 10}
    res = post_json('/techstore/api/products', payload)
    entries.append({'name': 'Crear producto válido', 'path': '/techstore/api/products', 'payload': payload, 'result': res})
    product_id = None
    if res.get('ok') and isinstance(res.get('response'), dict):
        resp = res.get('response')
        if 'result' in resp and isinstance(resp['result'], dict):
            product_id = resp['result'].get('id')
        else:
            product_id = resp.get('id') or resp.get('result')

    # 4) Crear producto con precio negativo (error esperado)
    payload = {'name': 'ProductoNeg', 'codigo': codigo_neg, 'precio_unitario': -5, 'stock_disponible': 5}
    res = post_json('/techstore/api/products', payload)
    entries.append({'name': 'Crear producto con precio negativo (error esperado)', 'path': '/techstore/api/products', 'payload': payload, 'result': res})

    # 5) Crear venta válida (si tenemos client_id y product_id)
    if client_id and product_id:
        payload = {'cliente_id': client_id, 'producto_id': product_id, 'cantidad': 2}
        res = post_json('/techstore/api/sales', payload)
        entries.append({'name': 'Crear venta válida', 'path': '/techstore/api/sales', 'payload': payload, 'result': res})
    else:
        entries.append({'name': 'Crear venta válida', 'path': '/techstore/api/sales', 'payload': None, 'result': {'ok': False, 'error': 'No se obtuvieron IDs de cliente/producto anteriores'}})

    # 6) Intentar venta que excede stock (usar cantidad grande)
    if client_id and product_id:
        payload = {'cliente_id': client_id, 'producto_id': product_id, 'cantidad': 9999}
        res = post_json('/techstore/api/sales', payload)
        entries.append({'name': 'Crear venta excediendo stock (error esperado)', 'path': '/techstore/api/sales', 'payload': payload, 'result': res})

    # 7) Consultar productos y ventas (GET)
    res = get_json('/techstore/api/products')
    entries.append({'name': 'Listar productos (GET)', 'path': '/techstore/api/products', 'payload': None, 'result': res})
    res = get_json('/techstore/api/sales')
    entries.append({'name': 'Listar ventas (GET)', 'path': '/techstore/api/sales', 'payload': None, 'result': res})

    # 8) Probar teléfono inválido (longitud)
    payload = {'name': 'Ana', 'cedula': cedula_ana, 'email': email_ana, 'telefono': '12345474'}
    res = post_json('/techstore/api/clients', payload)
    entries.append({'name': 'Crear cliente con teléfono inválido (error esperado)', 'path': '/techstore/api/clients', 'payload': payload, 'result': res})

    write_report(entries)


if __name__ == '__main__':
    run_tests()
