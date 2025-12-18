# T-Tech Autofollow SDK

[//]: # ([![PyPI]&#40;https://img.shields.io/pypi/v/ttech-autofollow-sdk&#41;]&#40;https://pypi.org/project/ttech-autofollow-sdk/&#41;)
[//]: # ([![PyPI - Python Version]&#40;https://img.shields.io/pypi/pyversions/ttech-autofollow-sdk&#41;]&#40;https://www.python.org/downloads/&#41;)
[//]: # (![GitHub]&#40;https://img.shields.io/github/license/RussianInvestments/python-autofollow-sdk&#41;)
[//]: # ([![PyPI Downloads]&#40;https://static.pepy.tech/badge/ttech-autofollow-sdk/month&#41;]&#40;https://pepy.tech/projects/ttech-autofollow-sdk&#41;)

Данный репозиторий предоставляет клиент для взаимодействия ведущих стратегий автоследования с API [Т-Инвестиций](https://www.tbank.ru/invest/) на языке Python.

- [Документация по API](https://developer.tbank.ru/invest/api/autofollow)

## Начало работы

<!-- terminal -->

```
$ pip install t-tech-autofollow
```

## Возможности

- REST клиент;
- получить список инструментов, доступных для автоследования;
- получить список стратегий автора;
- создать новый сигнал;
- создать отложенный сигнал;
- получить позицию портфеля для заданной стратегии;
- получить активные и отложенные сигналы;
- снять активные и отложенные сигналы.

## Как пользоваться

### Получить список стратегий автора

```python
from ttech_autofollow import Client

TOKEN = 'token'

with Client(access_token=TOKEN) as client:
    print(client.strategy_api.get_autofollow_strategies())
```

> :warning: **Не публикуйте токены в общедоступные репозитории**<br/><br/>
> Один из вариантов сохранения токена - использование [environment variables](https://github.com/RussianInvestments/python-autofollow-sdk/blob/main/examples/get_strategies.py).

Остальные примеры доступны в [examples](https://github.com/RussianInvestments/python-autofollow-sdk/blob/main/examples).


## License

Лицензия [The Apache License](https://github.com/RussianInvestments/python-autofollow-sdk/blob/main/LICENSE).
