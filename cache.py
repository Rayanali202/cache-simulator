class cacheLine:
    def __init__(self):
        self.bytes = '0' * 512
        self.tag = ""
        self.dirty = False

class L1:
    def __init__(self):
        self.data = [cacheLine() for _ in range(500)] # 32KB/64B
        self.instructions = [cacheLine() for _ in range(500)] # 32KB/64B

class L2:
    def __init__(self, assoc):
        # 256KB/64B/assoc = number of rows 
        # 4 cacheLines a row
        self.data = [[cacheLine() for _ in range(assoc)] for _ in range(int(4000/assoc))]


