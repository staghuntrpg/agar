class Logger:
    def __init__(self):
        pass

    def info(self, statement):
        print(statement)

    def error(self, statement):
        print('=================[error]=================\n')
        print(statement)