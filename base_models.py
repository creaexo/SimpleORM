""" В этом файле находятся базовые модели, которые будут использоваться для создания моделей пользователем """
import sqlite3

from base_models_exeptions import ErrorNotCorrectDB
from config import BaseOps


class OrmModel(BaseOps):
    """
        От этой модели наследуются все пользовательские модели
        :param db: Используемая база данных. Доступные значения находятся в классе DataBases.
        :param db_name: Имя используемой базы данных. Если её нет, будет создана.
        :param __init__: Метод, создающий словарь с именами и значениями наследуемых моделей.
        :param __str__: Когда от класса ожидается строка, возвращает название модели в нижнем регистре.
        :param create_table: Метод, создающий таблицу, название которой равно названию дочерней модели в нижнем
         регистре, а столбцы - это его атрибуты.
        :param save: Метод, реализующий запись в таблицу дочерней модели БД, где столбцы - это атрибуты класса,
         а значения - значения атрибутов.
        :param filter: Метод, позволяющий получить все записи таблицы, а также записи, соответствующие фильтру
         равенства. По умолчанию выводит только строки, подходящие параметры(Между ними логическое И).
         Задав аргумент _and_or=OR, будут выводиться все строки, которые подпадают хотя бы под одно условие (Между ними
         логическое ИЛИ). Добавив постфикс __exact к названию атрибута класса, для сравнения будет использоваться
         оператор LIKE, вместо =, которое используется по умолчанию.
         Так же можно использовать более сложные логические конструкции. Для этого нужно задать аргумент exact_query, в
         который в виде строки передаётся логическое выражение.
         Пример: SomeTable.filter(exact_query="some_field_2=2 AND (some_field_1='text3' OR some_field_3=50.0)")
        :param all: Метод, который возвращает все строки из таблицы модели.
    """
    db = BaseOps.db
    db_name = BaseOps.db_name

    def __init__(self, **kwargs):
        self.fields = {}
        for key, value in kwargs.items():
            self.fields[key] = value

    def __str__(self):
        return self.__name__.lower()

    @classmethod
    def create_table(cls):
        """ Метод, создающий таблицу, название которой равно названию дочерней модели в нижнем регистре. """
        if cls.db == 'sqlite':
            try:
                table_name = cls.__name__.lower()
                fields = [f"{field_name} {field_type}" for field_name, field_type in cls.__dict__.items() if
                          not field_name.startswith('__') and not callable(field_type)]
                pk_exists = False
                for index, field in enumerate(fields):
                    if 'PRIMARY KEY' in field:
                        pk_exists = True
                        print(f'{pk_exists=}')
                    if '.foreign_key.' in field:
                        fk_fields = field.split('.foreign_key.')
                        fields[index] = fk_fields[0]
                        first_fk = fk_fields[0].split(' ')[0]
                        table_fk_name = fk_fields[1].split('.')[0]
                        second_fk = fk_fields[1].split('.')[1]
                        fields.append(f'FOREIGN KEY ({first_fk}) REFERENCES {table_fk_name}({second_fk})')
                if pk_exists is False:
                    fields.insert(0, 'pk INTEGER PRIMARY KEY')
                print(fields)
                with sqlite3.connect(cls.db_name) as db_connect:
                    cursor = db_connect.cursor()
                    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(fields)})")
                    cursor.close()
            except Exception as E:
                raise E
        else:
            raise ErrorNotCorrectDB('Выбрана недоступная база данных. Проверьте значение db класса BaseOps в файле config.py')

    def save(self):
        """
            Метод, реализующий запись в таблицу дочерней модели БД, где столбцы - это атрибуты класса,
            а значения - значения атрибутов.
        """
        if self.db == 'sqlite':
            table_name = self.__class__.__name__.lower()
            fields = []
            values = []
            for field_name, field_value in self.fields.items():
                fields.append(field_name)
                values.append(field_value)
            with sqlite3.connect(self.db_name) as db_connect:
                cursor = db_connect.cursor()
                cursor.execute(
                    f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(['?'] * len(fields))})",
                    tuple(values)
                )
                cursor.close()
        else:
            raise ErrorNotCorrectDB('Выбрана недоступная база данных. Проверьте значение db класса BaseOps в файле config.py')

    @classmethod
    def filter(cls, **kwargs):
        """
            Метод, позволяющий получить все записи таблицы, а также записи, соответствующие фильтру
            равенства. По умолчанию выводит только строки, подходящие параметры(Между ними логическое И).
            Задав аргумент _and_or=OR, будут выводиться все строки, которые подпадают хотя бы под одно условие (Между ними
            логическое ИЛИ). Добавив постфикс __exact к названию атрибута класса, для сравнения будет использоваться
            оператор LIKE, вместо =, которое используется по умолчанию.
            Так же можно использовать более сложные логические конструкции. Для этого нужно задать аргумент exact_query, в
            который в виде строки передаётся логическое выражение.
            Пример: SomeTable.filter(exact_query="some_field_2=2 AND (some_field_1='text3' OR some_field_3=50.0)")
        """
        if cls.db == 'sqlite':
            table_name = cls.__name__.lower()
            conditions = []
            values = []
            exact_query = kwargs.get('exact_query')
            if exact_query is None:
                _and_or = 'AND'
                for field_name, field_value in kwargs.items():
                    if field_name == '_and_or':
                        _and_or = field_value
                        continue
                    operator = '='
                    if field_name.endswith('__exact'):
                        field_name = field_name[:-7]
                    else:
                        operator = 'LIKE'
                    conditions.append(f"{field_name} {operator} ?")
                    values.append(field_value)
                ex = f"SELECT * FROM {table_name} WHERE {f' {_and_or} '.join(conditions)}", tuple(values)
            else:
                ex = [f"SELECT * FROM {table_name} WHERE {exact_query}"]

            with sqlite3.connect(cls.db_name) as db_connect:
                cursor = db_connect.cursor()
                cursor.execute(*ex)
                rows = cursor.fetchall()
                cursor.close()
            return rows
        else:
            raise ErrorNotCorrectDB('Выбрана недоступная база данных. Проверьте значение db класса BaseOps в файле config.py')

    @classmethod
    def all(cls):
        """ Метод, который возвращает все строки из таблицы модели. """
        if cls.db == 'sqlite':
            table_name = cls.__name__.lower()
            with sqlite3.connect(cls.db_name) as db_connect:
                cursor = db_connect.cursor()
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                cursor.close()
            return rows
        else:
            raise ErrorNotCorrectDB(
                'Выбрана недоступная база данных. Проверьте значение db класса BaseOps в файле config.py')


class OrmText(BaseOps):
    """ Класс, возвращающий тип текста для команд в выбранную БД """
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        if BaseOps.db == 'sqlite':
            return 'TEXT'
        else:
            raise ErrorNotCorrectDB(
                'Выбрана недоступная база данных. Проверьте значение db класса BaseOps в файле config.py')


class OrmInteger(BaseOps):
    """ Класс, возвращающий тип целого числа для команд в выбранную БД """
    primary_key = False
    foreign_key_field = None

    def __init__(self, *args, **kwargs):
        self.primary_key = kwargs.get('primary_key')
        self.foreign_key_field = kwargs.get('foreign_key_field')
        pass

    def __str__(self):
        if BaseOps.db == 'sqlite':
            resource = 'INTEGER'
            if self.primary_key is True:
                resource += ' PRIMARY KEY'
            if self.foreign_key_field is not None:
                resource += f'.foreign_key.{self.foreign_key_field.lower()}'
                # print()
            return resource
        else:
            raise ErrorNotCorrectDB(
                'Выбрана недоступная база данных. Проверьте значение db класса BaseOps в файле config.py')


class OrmFloat(BaseOps):
    """ Класс, возвращающий тип дробного числа для команд в выбранную БД """
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        if BaseOps.db == 'sqlite':
            return 'REAL'
        else:
            raise ErrorNotCorrectDB(
                'Выбрана недоступная база данных. Проверьте значение db класса BaseOps в файле config.py')


class OrmBool(BaseOps):
    """ Класс, возвращающий логический тип для команд в выбранную БД """
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        if BaseOps.db == 'sqlite':
            return 'BLOB'
        else:
            raise ErrorNotCorrectDB(
                'Выбрана недоступная база данных. Проверьте значение db класса BaseOps в файле config.py')