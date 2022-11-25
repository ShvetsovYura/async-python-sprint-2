

class Promise:
    """ Класс хранит состояние вызова """

    def __get__(self, instance, owner):
        return instance.__dict__['result']

    def __set__(self, instance, value):
        instance.__dict__['result'] = value
