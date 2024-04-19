import hashlib
import cache
import random

class Simulator:
    def __init__(self):
        self.L1 = cache.L1()
        self.L2 = cache.L2()
        self.ran = 0
    
    '''def hash_L1(self, input_string):
        # Calculate the SHA-256 hash value of the input string from 0 - 9
        sha256_hash = hashlib.sha256(input_string.encode())
        hash_value = sha256_hash.hexdigest()
        hash_integer = int(hash_value, 16)
        mapped_value = hash_integer % 10
        return mapped_value

    def hash_L2(self, input_string):
        # Calculate the SHA-256 hash value of the input string from 0 - 999
        sha256_hash = hashlib.sha256(input_string.encode())
        hash_value = sha256_hash.hexdigest()
        hash_integer = int(hash_value, 16)
        mapped_value = hash_integer % 1000
        return mapped_value
    '''
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
        L1_rw = 0
        L2_rw = 0
        DRAM_rw = 0
        L1_hit = 0
        L2_hit = 0
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
                index_L2 = int(binaryAddress[-16:-6], 2) % 999
                tag_L1 = int(binaryAddress[:-15], 2)
                tag_L2 = int(binaryAddress[:-16], 2)

                if op == '0':
                    gotHit = False
                    # try L1 cache
                    time += 0.5
                    L1_rw += 1
                    if self.L1.data[index_L1].tag == tag_L1:
                        gotHit = True
                        L1_hit += 1
                        print("L1")

                    # try L2 cache
                    if not gotHit:
                        time += 5
                        L2_rw += 1
                        for cLine in self.L2.data[index_L2]:
                            if cLine.tag == tag_L2:
                                gotHit = True
                                L2_hit += 1
                                # swap data in L1 & L2
                                oldL1_tag = str(self.L1.data[index_L1].tag)
                                oldL1_bytes = str(self.L1.data[index_L1].bytes)
                                oldL1_dirty = str(self.L1.data[index_L1].dirty)

                                # *** figure out write timing

                                self.L1.data[index_L1].tag = cLine.tag
                                self.L1.data[index_L1].bytes = cLine.bytes
                                self.L1.data[index_L1].dirty = cLine.dirty

                                cLine.tag = oldL1_tag
                                cLine.bytes = oldL1_bytes
                                cLine.dirty = oldL1_dirty
                                break

                    # have to go to DRAM & store in L2
                    if not gotHit:
                        time += 50
                        DRAM_rw += 1
                        stored = False
                        for cLine in self.L2.data[index_L2]:
                            # check for empty
                            if cLine.tag == "":
                                stored = True
                                time += 5
                                cLine.tag = tag_L2
                                cLine.bytes = value
                                break
                        # empty spot not found replace random cache line
                        if not stored:
                            time += 5
                            idx = random.randint(0, 3)
                            self.ran += 1
                            # *** figure out wrtie timing
                            if self.L2.data[index_L2][idx].dirty:
                                print("WRITE BACK TO MEMORY")
                            self.L2.data[index_L2][idx].tag = tag_L2
                            self.L2.data[index_L2][idx].bytes = value
                            self.L2.data[index_L2][idx].dirty = False

                elif op == '1':
                    gotHit = False
                    # try L1 cache
                    time += 0.5
                    L1_rw += 1
                    if self.L1.data[index_L1].tag == tag_L1:
                        gotHit = True
                        L1_hit += 1
                        self.L1.data[index_L1].bytes = value
                        self.L1.data[index_L1].dirty = True

                    # try L2 cache
                    if not gotHit:
                        time += 5
                        L2_rw += 1
                        for cLine in self.L2.data[index_L2]:
                            if cLine.tag == tag_L2:
                                gotHit = True
                                L2_hit += 1
                                # swap data in L1 & L2
                                oldL1_tag = str(self.L1.data[index_L1].tag)
                                oldL1_bytes = str(self.L1.data[index_L1].bytes)
                                oldL1_dirty = str(self.L1.data[index_L1].dirty)

                                # *** figure out write timing
                                # *** update value in cLine.bytes
                                self.L1.data[index_L1].tag = cLine.tag
                                self.L1.data[index_L1].bytes = cLine.bytes
                                self.L1.data[index_L1].dirty = True

                                cLine.tag = oldL1_tag
                                cLine.bytes = oldL1_bytes
                                cLine.dirty = oldL1_dirty
                                break

                    # have to go to DRAM & store in L2
                    if not gotHit:
                        time += 50
                        DRAM_rw += 1
                        stored = False
                        for cLine in self.L2.data[index_L2]:
                            # check for empty
                            if cLine.tag == "":
                                stored = True
                                time += 5
                                cLine.tag = tag_L2
                                cLine.bytes = value
                                break
                        # empty spot not found replace random cache line
                        if not stored:
                            idx = random.randint(0, 3)
                            self.ran += 1
                            if self.L2.data[index_L2][idx].dirty:
                                print("WRITE BACK TO MEMORY")
                            time += 5
                            self.L2.data[index_L2][idx].tag = tag_L2
                            self.L2.data[index_L2][idx].bytes = value
                            self.L2.data[index_L2][idx].dirty = False

                elif op == '2':
                    gotHit = False
                    # try L1 cache
                    time += 0.5
                    L1_rw += 1
                    if self.L1.instructions[index_L1].tag == tag_L1:
                        gotHit = True
                        L1_hit += 1
                    
                    # check DRAM for instruction & store in L1
                    if not gotHit:
                        time += 50
                        DRAM_rw += 1
                        time += 0.5
                        self.L1.instructions[index_L1].tag = tag_L1
                        self.L1.instructions[index_L1].bytes = value

                elif op == '3':
                    print("IGNORE")

                elif op == '4':
                    print("IGNORE")
                    
        print(time)
        L1_idle = (time - 0.5 * L1_rw)/0.5
        L1_energy = L1_idle * 0.5 + L1_rw * 1
        L2_idle = (time - 5 * L2_rw)/5
        L2_energy = L2_idle * 0.8 + L2_rw * 2
        DRAM_idle = (time - 50 * L1_rw)/50
        DRAM_energy = DRAM_idle * 0.8 + DRAM_rw * 4

        print(L1_energy + L2_energy + DRAM_energy)
        print("L1 COUNT: ", L1_rw)
        print("L2 COUNT: ", L2_rw)
        print("DRAM COUNT: ", DRAM_rw)
        print("RANDOM: ", self.ran)
        print("L1 HIT RATE: ", L1_hit/L1_rw)
        print("L2 HIT: ", L2_hit/L2_rw)



sim = Simulator()
sim.simulate('013.spice2g6.din')