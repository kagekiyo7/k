import sys
import re
import os

def main():
    with open(sys.argv[1], "rb") as inf:
        data = inf.read()
    with open(re.sub(r"\.bin$", ".oob", sys.argv[1]), "rb") as inf:
        oob = inf.read()

    output = os.path.join(
        os.path.dirname(sys.argv[1]),
        f"{os.path.splitext(os.path.basename(sys.argv[1]))[0]}_remapped.bin"
    )

    assert len(data) % 512 == 0
    assert len(oob) % 16 == 0
    assert (len(oob) // 16) * 512 == len(data)

    data_sector_size = 0x200
    oob_sector_size = 0x10

    data_block_size = data_sector_size * 0x20
    oob_block_size = oob_sector_size * 0x20
    
    
    chunk_dicts = []
    matched = set()
    for block in range(len(oob)//oob_block_size):
        data_block = data[block * data_block_size : (block+1) * data_block_size]
        oob_block = oob[block * oob_block_size : (block+1) * oob_block_size]

        if oob_block == b"\xFF" * oob_block_size:
            continue

        block_id = int.from_bytes(oob_block[0x6:0x8], "big") & 0x0FFF
        if block_id in matched:
            print(f"WARN: duplicate block id (Block id: {hex(block_id)}, OOB offset: {hex(block * oob_block_size)})")
        else:
            temp_fat = bytearray()
            for sector in range(oob_block_size // oob_sector_size):
                temp_oob = oob_block[sector * oob_sector_size : (sector+1) * oob_sector_size]
                if temp_oob[0x8:0xB] != b"\xFF" * 3 or temp_oob[0xC:oob_sector_size] != b"\xFF" * 3:
                    temp_fat += data_block[sector * data_sector_size : (sector+1) * data_sector_size]
            chunk_dicts.append({"fat": temp_fat, "block_id": block_id})
        matched.add(block_id)
        

    
    fat = bytearray()
    for chunk_dict in sorted(chunk_dicts, key=lambda x:x["block_id"]):
        print(hex(chunk_dict["block_id"]))
        fat += chunk_dict["fat"]
        
    # for chunk_dict in sorted(chunk_dicts, key=lambda x:x["block_id"]):
        # print(hex(chunk_dict["block_id"]))
        # fat += chunk_dict["fat"]
            
    with open(output, "wb") as outf:
        outf.write(fat)

if __name__ == "__main__":
    main()
