# Cache Simulator

Program starts by converting hex address to a 32 bit binary string. Starting from the right the first 6 bits are the offset bits for the 64B cache line. The next 9 bits represent the L1 cache index and the next 10 (could be 9 or 11 based on set associativity) represent the L2 cache index. The remaining bits are the Tag bits.

![Image Alt Text](images/bits.png)

**Code Explanation**
The logic behind the cache simulator occurs in the 'simulate()' function in the Simulator class.

**Read:**
In the case of a read we start by checking the L1 cache at the L1_index for a tag match, this takes 0.5nsec. In the case of a miss, we go to the L2 cache at the L2_index and check for a tag match in the set. This takes 4.5nsec and in the case of a hit we incur a penalty of 5pj for moving the cache line into the L1 cache. If both L1 and L2 miss then we go to DRAM, which takes 45nsec. We check for an empty spot in the L2 cache in the set at L2_index. If no empty spot is found we choose a random cache line to replace. Moving data from DRAM to L2 or from L2 to DRAM (in the case of a dirty eviction) incurs a penalty of 640pj. Additionally, since we have an inclusive cache we have to make sure that the cache line we just evicted from L2 does not also currently exist in L1. In order to remedy this, we replace whatever is at L1_index with the new cache line brought in from DRAM and stored in L2. This takes a 5pj penalty for moving data from L2 to L1. 

**Write:**
Writes works pretty similar to reads with slight differences. We start by checking L1 for a tag match. If we get a hit this takes 5nsec (0.5nsec for L1 and 4.5 for L2) since we have to write through to L2. If we miss we go to L2. If we get a hit on the L2 cache then we write to L2 and move the updated cache line up to L1, we also mark the cache line as dirty and it takes 5nsec total. We also incur a 5pj penalty for moving data from L2 to L1. If both L1 and L2 miss we bring the cache line in from DRAM and replace a cache line in L2. We also update the respective cache line in L1 with the newly brought in cache line to maintain inclusivity. This takes no time according to specifications on Ed Discussion but we incur a penalty of 640pj for moving data between DRAM and L2 and 5pj for moving data between L2 and L1.

# Results 

**2 Set Associativity**
![Image Alt Text](images/2sets1.png)
![Image Alt Text](images/2sets2.png)

**4 Set Associativity**
![Image Alt Text](images/4sets1.png)
![Image Alt Text](images/4sets2.png)

**8 Set Associativity**
![Image Alt Text](images/8sets1.png)
![Image Alt Text](images/8sets2.png)
