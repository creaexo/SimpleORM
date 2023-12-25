""" Здесь создаются пользовательские модели и происходит взаимодействие с ними """
from base_models import OrmModel, OrmInteger, OrmText, OrmFloat


class SomeTable1(OrmModel):
    pk = OrmInteger(primary_key=True)
    field = OrmInteger()


class SomeTable2(OrmModel):
    some_field_1 = OrmText()
    some_field_2 = OrmInteger(foreign_key_field='SomeTable1.field')
    some_field_3 = OrmFloat()


if __name__ == '__main__':
    SomeTable1.create_table()
    SomeTable2.create_table()
    SomeTable1(field=1).save()
    SomeTable1(field=2).save()
    SomeTable2(some_field_1='text', some_field_2=1, some_field_3=5.0).save()
    SomeTable2(some_field_1='text2', some_field_2=2, some_field_3=30.0).save()
    SomeTable2(some_field_1='text3', some_field_2=2, some_field_3=50.0).save()
    SomeTable2(some_field_1='text4', some_field_2=2, some_field_3=50.0).save()
    SomeTable2(some_field_1='text5', some_field_2=1, some_field_3=50.0).save()
    print(SomeTable2.filter(some_field_1='text3', some_field_2=2, some_field_3=50.0, _and_or='AND'))
    print(SomeTable2.filter(some_field_1='text3', some_field_2=2, some_field_3=50.0, _and_or='OR'))
    print(SomeTable2.filter(exact_query="some_field_2=2 AND (some_field_1='text3' OR some_field_3=50.0)"))
    print(SomeTable2.all())
