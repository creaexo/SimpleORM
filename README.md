# SimpleORM
***
Это простая ORM модель, для взаимодействия с БД, с помощью Python. Пока что, реализовано взаимодействие только с sqlite, 
в будущем могут быть добавлены другие.

## Структура
*Базовые модели с основной логикой* - [base_models.py](base_models.py)

*Классы исключений* - [base_models_exeptions.py](base_models_exeptions.py)

*Конфигурация, которую настраивает пользователь* - [config.py](config.py)

*Пользовательские модели* - [main.py](main.py)

## Настройка
В файле [config.py](config.py) выбираем нужную БД и классу BaseOps присваиваем соответствующее значение в атрибут db,
также присваиваем значение атрибуту db_name, записав в него название БД.

## Пример использования
После настройки конфигурации, работаем в файле [main.py](main.py)
```python
from base_models import OrmModel, OrmInteger, OrmText, OrmFloat

# Создаём класс первой модели
class SomeTable1(OrmModel):
    pk = OrmInteger(primary_key=True)
    field = OrmInteger()

# Создаём класс второй модели
class SomeTable2(OrmModel):
    some_field_1 = OrmText()
    some_field_2 = OrmInteger(foreign_key_field='SomeTable1.field')
    some_field_3 = OrmFloat()

    
# Создаём таблицы классов моделей
SomeTable1.create_table() 
SomeTable2.create_table() 

# Вносим записи в таблицы
SomeTable1(field=1).save() 
SomeTable1(field=2).save()
SomeTable2(some_field_1='text', some_field_2=1, some_field_3=5.0).save()
SomeTable2(some_field_1='text2', some_field_2=2, some_field_3=30.0).save()
SomeTable2(some_field_1='text3', some_field_2=2, some_field_3=50.0).save()
SomeTable2(some_field_1='text4', some_field_2=2, some_field_3=50.0).save()
SomeTable2(some_field_1='text5', some_field_2=1, some_field_3=50.0).save()

# Получаем данные из таблицы с различными фильтрами и без
print(SomeTable2.filter(some_field_1='text3', some_field_2=2, some_field_3=50.0, _and_or='AND'))
print(SomeTable2.filter(some_field_1='text3', some_field_2=2, some_field_3=50.0, _and_or='OR'))
print(SomeTable2.filter(exact_query="some_field_2=2 AND (some_field_1='text3' OR some_field_3=50.0)"))
print(SomeTable2.all())
```
~~~
>>>[(3, 'text3', 2, 50.0)]
>>>[(2, 'text2', 2, 30.0), (3, 'text3', 2, 50.0), (4, 'text4', 2, 50.0), (5, 'text5', 1, 50.0)]
>>>[(3, 'text3', 2, 50.0), (4, 'text4', 2, 50.0)]
>>>[(1, 'text', 1, 5.0), (2, 'text2', 2, 30.0), (3, 'text3', 2, 50.0), (4, 'text4', 2, 50.0), (5, 'text5', 1, 50.0)]
~~~