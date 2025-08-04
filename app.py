# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import os

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,POST,OPTIONS")
        return response

# Базовая авторизация для внешнего API
AUTH_TOKEN = "client_site_zni:UtYf#8_5eWSd"
AUTH_HEADER = base64.b64encode(AUTH_TOKEN.encode()).decode()

# URL внешнего API
EXTERNAL_API_URL = "https://betaportal.nomadlife.kz:8082/ords/cab/ws/gons/calculate2"

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """
    Прокси для калькулятора страхования
    
    Ожидаемые параметры в JSON:
    {
        "p_bd": "18.08.1995",      # Дата рождения
        "p_val": 3,                # Значение
        "p_susn": 0,               # Параметр SUSN
        "p_ins_prem": 10,          # Страховая премия
        "p_term": 11,              # Срок
        "p_period": 12             # Период
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Нет данных в запросе"}), 400
        
        # Обязательные параметры
        required_params = ['p_bd', 'p_val']
        for param in required_params:
            if param not in data:
                return jsonify({"error": f"Отсутствует обязательный параметр: {param}"}), 400
        
        # Подготовка параметров для внешнего API
        params = {
            'p_bd': data.get('p_bd'),
            'p_val': data.get('p_val', 1),
            'p_susn': data.get('p_susn', 0),
            'p_ins_prem': data.get('p_ins_prem', 10),
            'p_term': data.get('p_term', 11),
            'p_period': data.get('p_period', 12)
        }
        
        print(f"📊 Запрос к калькулятору с параметрами: {params}")
        
        # Заголовки для внешнего API
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {AUTH_HEADER}'
        }
        
        # Формируем данные для отправки
        form_data = {}
        for key, value in params.items():
            form_data[key] = str(value)
        
        # Выполняем запрос к внешнему API
        try:
            response = requests.get(
                EXTERNAL_API_URL,
                params=params,
                headers=headers,
                timeout=30,
                verify=False  # Отключаем проверку SSL для избежания проблем
            )
            
            print(f"📡 Ответ от внешнего API: статус {response.status_code}")
            print(f"📄 Содержимое ответа: {response.text[:500]}...")
            
            if response.status_code == 200:
                try:
                    # Пытаемся распарсить JSON ответ
                    external_data = response.json()
                    
                    return jsonify({
                        "success": True,
                        "data": external_data,
                        "meta": {
                            "proxy_service": "calculator-service",
                            "external_api": "betaportal.nomadlife.kz",
                            "request_params": params
                        }
                    })
                    
                except ValueError as e:
                    # Если JSON не валидный, возвращаем текст
                    return jsonify({
                        "success": True,
                        "data": {
                            "raw_response": response.text,
                            "content_type": response.headers.get('content-type', 'unknown')
                        },
                        "meta": {
                            "proxy_service": "calculator-service",
                            "external_api": "betaportal.nomadlife.kz",
                            "request_params": params,
                            "note": "Response is not valid JSON"
                        }
                    })
            else:
                return jsonify({
                    "success": False,
                    "error": f"Внешний API вернул ошибку: {response.status_code}",
                    "details": response.text[:1000]
                }), response.status_code
                
        except requests.exceptions.SSLError as e:
            print(f"🔒 SSL ошибка: {str(e)}")
            return jsonify({
                "success": False,
                "error": "SSL ошибка при подключении к внешнему API",
                "details": str(e)
            }), 502
            
        except requests.exceptions.Timeout as e:
            print(f"⏰ Таймаут: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Таймаут при обращении к внешнему API",
                "details": str(e)
            }), 504
            
        except requests.exceptions.RequestException as e:
            print(f"🌐 Ошибка сети: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Ошибка сети при обращении к внешнему API",
                "details": str(e)
            }), 502
        
    except Exception as e:
        print(f"❌ ОБЩАЯ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Внутренняя ошибка прокси-сервера: {str(e)}"
        }), 500

@app.route('/api/calculate-simple', methods=['POST'])
def calculate_simple():
    """
    Упрощенный endpoint для калькулятора
    
    Ожидаемые параметры:
    {
        "birthdate": "18.08.1995",
        "value": 3
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Нет данных в запросе"}), 400
        
        birthdate = data.get('birthdate')
        value = data.get('value', 1)
        
        if not birthdate:
            return jsonify({"error": "Отсутствует параметр birthdate"}), 400
        
        # Преобразуем в формат, который ожидает внешний API
        calc_data = {
            "p_bd": birthdate,
            "p_val": value,
            "p_susn": 0,
            "p_ins_prem": 10,
            "p_term": 11,
            "p_period": 12
        }
        
        # Создаем новый request с нужными данными
        import json
        from werkzeug.test import EnvironBuilder
        from flask import Flask
        
        builder = EnvironBuilder(method='POST', data=json.dumps(calc_data), content_type='application/json')
        env = builder.get_environ()
        
        with app.request_context(env):
            return calculate()
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Ошибка в упрощенном калькуляторе: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "OK", 
        "service": "calculator-proxy-service",
        "external_api": "betaportal.nomadlife.kz:8082"
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "Calculator Proxy Service",
        "description": "Прокси-сервис для калькулятора страхования",
        "endpoints": {
            "/api/calculate": "POST - Полный калькулятор",
            "/api/calculate-simple": "POST - Упрощенный калькулятор",
            "/health": "GET - Проверка работоспособности"
        },
        "external_api": "https://betaportal.nomadlife.kz:8082/ords/cab/ws/gons/calculate2",
        "example_request": {
            "url": "/api/calculate",
            "method": "POST",
            "body": {
                "p_bd": "18.08.1995",
                "p_val": 3,
                "p_susn": 0,
                "p_ins_prem": 10,
                "p_term": 11,
                "p_period": 12
            }
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5004))
    print(f"🧮 Запуск Calculator Proxy Service на порту {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
