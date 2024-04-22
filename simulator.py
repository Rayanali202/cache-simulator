import cache
import random
import statistics

class Simulator:
    def __init__(self, assoc):
        self.associativity = int(assoc)
        self.L1 = cache.L1()
        self.L2 = cache.L2(self.associativity)
        self.ran = 0
    
    def hexToBinary(self, hex_string):
        binary_string = ""

        # Convert each hexadecimal digit to binary and concatenate
        for hex_digit in hex_string:
            # Convert hexadecimal digit to binary string
            binary_digit = bin(int(hex_digit, 16))[2:].zfill(4)  # Convert to binary and zero-pad to 4 bits
            # Concatenate binary digit to the result
            binary_string += binary_digit

        binary_string = binary_string.zfill(32)

        return binary_string

    
    def simulate(self, file_name):
        time = 0
        async_time = 0
        L1_try = 0
        L2_try = 0
        L1_rw = 0
        L2_rw = 0
        DRAM_rw = 0
        L1_hit = 0
        L2_hit = 0
        penalty = 0
        with open(file_name, 'r') as file:
            for line in file:
                # Split the line into individual values
                values = line.strip().split()
                op = values[0]
                curAddress = values[1]
                value = values[2]

                binaryAddress = self.hexToBinary(values[1])
                offset = binaryAddress[-6:]
                index_L1 = int(binaryAddress[-15:-6], 2) % 499
                index_L2 = int(binaryAddress[-16:-6], 2) % (int(4000/self.associativity) - 1)
                tag_L1 = int(binaryAddress[:-15], 2)
                tag_L2 = int(binaryAddress[:-16], 2)

                if op == '0':
                    gotHit = False
                    # try L1 cache
                    L1_try += 1
                    L1_rw += 1
                    if self.L1.data[index_L1].tag == tag_L1:
                        time += 0.5
                        gotHit = True
                        L1_hit += 1

                    # try L2 cache
                    if not gotHit:
                        L2_try += 1
                        L2_rw += 1
                        for cLine in self.L2.data[index_L2]:
                            if cLine.tag == tag_L2:
                                time += 5
                                penalty += 5
                                gotHit = True
                                L2_hit += 1

                                # move cache line up to L1
                                self.L1.data[index_L1].tag = tag_L1
                                self.L1.data[index_L1].bytes = cLine.bytes
                                self.L1.data[index_L1].dirty = cLine.dirty
                                break

                    # have to go to DRAM & store in L2 and L1
                    if not gotHit:
                        time += 50
                        penalty += 5 + 640
                        DRAM_rw += 1
                        stored = False
                        for cLine in self.L2.data[index_L2]:
                            # check for empty
                            if cLine.tag == "":
                                stored = True
                                cLine.tag = tag_L2
                                cLine.bytes = value
                                self.L1.data[index_L1].tag = tag_L1
                                self.L1.data[index_L1].bytes = value
                                self.L1.data[index_L1].dirty = False
                                break
                        # empty spot not found replace random cache line
                        if not stored:
                            time += 5
                            idx = random.randint(0, 3)
                            self.ran += 1
                            # *** figure out write timing
                            '''if self.L2.data[index_L2][idx].dirty:
                                print("GOt")'''
                            self.L2.data[index_L2][idx].tag = tag_L2
                            self.L2.data[index_L2][idx].bytes = value
                            self.L2.data[index_L2][idx].dirty = False
                            self.L1.data[index_L1].tag = tag_L1
                            self.L1.data[index_L1].bytes = value
                            self.L1.data[index_L1].dirty = False

                elif op == '1':
                    gotHit = False
                    # try L1 cache
                    L1_try += 1
                    L1_rw += 1
                    if self.L1.data[index_L1].tag == tag_L1:
                        async_time = max(async_time, time + 5)
                        L2_rw += 1
                        gotHit = True
                        L1_hit += 1
                        self.L1.data[index_L1].bytes = value
                        self.L1.data[index_L1].dirty = True
                        # write through to L2 cache
                        for cLine in self.L2.data[index_L2]:
                            # check for match
                            if cLine.tag == tag_L2:
                                cLine.bytes = value
                                cLine.dirty = True
                                break

                    # try L2 cache
                    if not gotHit:
                        L2_try += 1
                        L2_rw += 1
                        for cLine in self.L2.data[index_L2]:
                            if cLine.tag == tag_L2:
                                async_time = max(async_time, time + 5)
                                gotHit = True
                                L2_hit += 1
                                penalty += 5

                                cLine.bytes = value
                                cLine.dirty = True
                                self.L1.data[index_L1].tag = tag_L1
                                self.L1.data[index_L1].bytes = cLine.bytes
                                self.L1.data[index_L1].dirty = True
                                break

                    # have to go to DRAM & store in L2
                    if not gotHit:
                        stored = False
                        penalty += 5 + 640
                        for cLine in self.L2.data[index_L2]:
                            # check for empty
                            if cLine.tag == "":
                                stored = True
                                cLine.tag = tag_L2
                                cLine.bytes = value
                                self.L1.data[index_L1].tag = tag_L1
                                self.L1.data[index_L1].bytes = value
                                self.L1.data[index_L1].dirty = False
                                break
                        # empty spot not found replace random cache line
                        if not stored:
                            idx = random.randint(0, self.associativity - 1)
                            self.ran += 1
                            '''if self.L2.data[index_L2][idx].dirty:
                                print("WRITE BACK TO MEMORY")'''
                            self.L2.data[index_L2][idx].tag = tag_L2
                            self.L2.data[index_L2][idx].bytes = value
                            self.L2.data[index_L2][idx].dirty = False
                            self.L1.data[index_L1].tag = tag_L1
                            self.L1.data[index_L1].bytes = value
                            self.L1.data[index_L1].dirty = False

                elif op == '2':
                    gotHit = False
                    # try L1 cache
                    L1_try += 1
                    L1_rw += 1
                    if self.L1.instructions[index_L1].tag == tag_L1:
                        time += 0.5
                        gotHit = True
                        L1_hit += 1
                    
                    # try L2 cache
                    if not gotHit:
                        L2_try += 1
                        L2_rw += 1
                        for cLine in self.L2.data[index_L2]:
                            if cLine.tag == tag_L2:
                                time += 5
                                penalty += 5
                                gotHit = True
                                L2_hit += 1

                                # move cache line up to L1
                                self.L1.instructions[index_L1].tag = tag_L1
                                self.L1.instructions[index_L1].bytes = cLine.bytes
                                self.L1.instructions[index_L1].dirty = cLine.dirty
                                break
                    
                    # have to go to DRAM & store in L2
                    if not gotHit:
                        time += 50
                        DRAM_rw += 1
                        penalty += 5 + 640
                        stored = False
                        for cLine in self.L2.data[index_L2]:
                            # check for empty
                            if cLine.tag == "":
                                stored = True
                                cLine.tag = tag_L2
                                cLine.bytes = value
                                self.L1.instructions[index_L1].tag = tag_L1
                                self.L1.instructions[index_L1].bytes = value
                                self.L1.instructions[index_L1].dirty = False
                                break
                        # empty spot not found replace random cache line
                        if not stored:
                            idx = random.randint(0, self.associativity - 1)
                            self.ran += 1
                            '''if self.L2.data[index_L2][idx].dirty:
                                print("WRITE BACK TO MEMORY")'''
                            self.L2.data[index_L2][idx].tag = tag_L2
                            self.L2.data[index_L2][idx].bytes = value
                            self.L2.data[index_L2][idx].dirty = False
                            self.L1.instructions[index_L1].tag = tag_L1
                            self.L1.instructions[index_L1].bytes = value
                            self.L1.instructions[index_L1].dirty = False
                elif op == '3':
                    print("IGNORE")

                elif op == '4':
                    print("IGNORE")

        return L1_try, L1_hit, L2_try, L2_hit, L1_rw, L2_rw, DRAM_rw, max(time, async_time)


if __name__ == "__main__":
    file_names = ['008.espresso.din', '013.spice2g6.din', '022.li.din', '026.compress.din', '048.ora.din', '085.gcc.din']
    for name in file_names:
        print("-------------------------------------------")
        print(name.upper())
        print()
        L1HitRate = []
        L2HitRate = []
        L1StaticEnergy = []
        L2StaticEnergy = []
        DRAMStaticEnergy = []
        L1ActiveEnergy = []
        L2ActiveEnergy = []
        DRAMActiveEnergy = []
        for i in range(1, 11):
            print(i,"/10")
            sim = Simulator(4)
            L1_try, L1_hit, L2_try, L2_hit, L1_rw, L2_rw, DRAM_rw, time = sim.simulate(name)
            L1HitRate.append(L1_hit/L1_try)
            L2HitRate.append(L2_hit/L2_try)

            L1_active_time = L1_rw * 0.5
            L1ActiveEnergy.append(L1_active_time * 1)
            L1_static_time = time - L1_active_time
            L1StaticEnergy.append(L1_static_time * 0.5)

            L2_active_time = L2_rw * 4.5
            L2ActiveEnergy.append(L2_active_time * 2)
            L2_static_time = time - L2_active_time
            L2StaticEnergy.append(L2_static_time * 0.8)

            DRAM_active_time = DRAM_rw * 45
            DRAMActiveEnergy.append(DRAM_active_time * 4)
            DRAM_static_time = time - DRAM_active_time
            DRAMStaticEnergy.append(DRAM_static_time * 0.8)

            print(time)

        print("Avg L1 Hit Rate: ", statistics.mean(L1HitRate),"-------- Std Dev: ", statistics.stdev(L1HitRate))
        print("Avg L2 Hit Rate: ", statistics.mean(L2HitRate),"-------- Std Dev: ", statistics.stdev(L2HitRate))
        print()
        print("Avg L1 Active Energy: ", statistics.mean(L1ActiveEnergy),"-------- Std Dev: ", statistics.stdev(L1ActiveEnergy))
        print("Avg L1 Static Energy: ", statistics.mean(L1StaticEnergy),"-------- Std Dev: ", statistics.stdev(L1StaticEnergy))
        print()
        print("Avg L2 Active Energy: ", statistics.mean(L2ActiveEnergy),"-------- Std Dev: ", statistics.stdev(L2ActiveEnergy))
        print("Avg L2 Static Energy: ", statistics.mean(L2StaticEnergy),"-------- Std Dev: ", statistics.stdev(L2StaticEnergy))
        print()
