import sys
import os

structures = [[512, 16], [1024, 32], [2048, 64], [4096, 128], [8192, 256]]



def main():
    for structure in structures:
        nand_pagesize = structure[0]
        oob_pagesize = structure[1]
        
        nand = sys.argv[1]
        nandname = os.path.splitext(os.path.basename(nand))[0]
        out_nand = os.path.join(os.path.dirname(nand), f"separated_{nandname}_{str(nand_pagesize)}.bin")
        out_oob = os.path.join(os.path.dirname(nand), f"separated_{nandname}_{str(nand_pagesize)}.oob")
        print(f"nand: {nand}")
        
        with open(nand, "rb") as in_nandf:
            #if len(in_nandf.read()) % NAND_BYTE_STEP+OOB_BYTE_STEP != 0: raise ValueError("The nand size is not appropriate.")
            with open(out_nand, "wb") as out_nandf:
                with open(out_oob, "wb") as out_oobf:
                    while True:
                        nand_temp = in_nandf.read(nand_pagesize)
                        if not nand_temp: break
                        oob_temp = in_nandf.read(oob_pagesize)
                        if not oob_temp: break
                        out_nandf.write(nand_temp)
                        out_oobf.write(oob_temp)
                    print("succeed")


if __name__ == "__main__":
    main()