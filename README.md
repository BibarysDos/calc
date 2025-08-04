# Calculator Proxy Service

Прокси-сервис для работы с калькулятором страхования от betaportal.nomadlife.kz

## Описание

Этот сервис является прокси между клиентским приложением и внешним API калькулятора страхования. Он решает проблемы CORS и обеспечивает единообразный интерфейс для работы с калькулятором.

## API Endpoints

### POST /api/calculate
Полный калькулятор с всеми параметрами

**Параметры:**
```json
{
  "p_bd": "18.08.1995",      // Дата рождения (обязательно)
  "p_val": 3,                // Значение (обязательно)
  "p_susn": 0,               // Параметр SUSN (по умолчанию 0)
  "p_ins_prem": 10,          // Страховая премия (по умолчанию 10)
  "p_term": 11,              // Срок (по умолчанию 11)
  "p_period": 12             // Период (по умолчанию 12)
}
```

### POST /api/calculate-simple
Упрощенный калькулятор

**Параметры:**
```json
{
  "birthdate": "18.08.1995", // Дата рождения
  "value": 3                 // Значение
}
```

### GET /health
Проверка работоспособности сервиса

### GET /
Информация о сервисе и примеры использования

## Пример использования

```javascript
// Полный калькулятор
const response = await fetch('https://your-calculator-service.onrender.com/api/calculate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    p_bd: '18.08.1995',
    p_val: 3,
    p_susn: 0,
    p_ins_prem: 10,
    p_term: 11,
    p_period: 12
  })
});

const result = await response.json();
console.log(result);
```

## Внешний API

Сервис обращается к: `https://betaportal.nomadlife.kz:8082/ords/cab/ws/gons/calculate2`

## Деплой на Render

1. Создайте новый веб-сервис на Render.com
2. Подключите GitHub репозиторий
3. Укажите папку `calculator-service-deploy` как корневую
4. Render автоматически обнаружит Python приложение

## Переменные окружения

- `PORT` - порт для запуска (устанавливается автоматически Render)
- `PYTHON_VERSION` - версия Python (3.9.16)

## Особенности

- Автоматическая обработка CORS
- Обработка SSL сертификатов
- Детальное логирование запросов
- Обработка различных форматов ответов от внешнего API
- Таймауты и обработка ошибок сети
