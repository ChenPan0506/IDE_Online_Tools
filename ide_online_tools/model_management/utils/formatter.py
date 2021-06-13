
class Formatter:
    @staticmethod
    def formatter(src: str, firstUpper: bool = True):
        """
        将下划线分隔的名字,转换为驼峰模式
        :param src: test_date
        :param firstUpper: 转换后的首字母是否指定大写(  testDate or  TestDate)
        :return:testDate
        """
        arr = src.split('_')
        res = ''
        for i in arr:
            res = res + i[0].upper() + i[1:]

        if not firstUpper:
            res = res[0].lower() + res[1:]
        return res
