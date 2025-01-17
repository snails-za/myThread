class Febinacci(object):
    def __init__(self, all_num):
        self.current_num = 0
        self.all_num = all_num
        self.a = 0
        self.b = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_num < self.all_num:
            ret = self.a
            self.a, self.b = self.b, self.a + self.b
            self.current_num += 1
            return ret
        else:
            raise StopIteration

febo = Febinacci(10)


for num in febo:
    print(num)







