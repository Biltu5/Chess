ranksToRows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4,
                   "5" : 3, "6" : 2, "7" : 1,"8" : 0}
rowsToRanks = {v: k for k , v in ranksToRows.items()}
filesToCols = {"a" : 0, "b" : 1, "c" : 3, "d" : 4,
                   "e" : 5, "f" : 6, "g" : 7, "h" : 8}
colsToFiles = {v: k for k ,v in filesToCols.items()}
# print(filesToCols)
# print(colsToFiles)
# print(ranksToRows)
# print(rowsToRanks)

class test:
    def hi(self,a):
        a.append('hi')
    def getSomething(self):
        a = []
        self.hi(a)
        return a
a=test()
#print(a.getSomething())
a = ['1','2','3','4','5','6']
#print(a[-1])
