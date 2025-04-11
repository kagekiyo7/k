import sys
import re
import os

def main():
    with open(sys.argv[1], "rb") as inf:
        data = inf.read()
    with open(re.sub(r"\.bin$", ".oob", sys.argv[1]), "rb") as inf:
        oob = inf.read()

    output = sys.argv[1] + "_fat.bin"

    assert len(data) % 512 == 0
    assert len(oob) % 16 == 0
    assert (len(oob) // 16) * 512 == len(data)


    data_page_size = 0x200 * 0x20
    oob_page_size = 0x10 * 0x20
    
    
    chunk_dicts = []
    matched = set()
    for page in range(len(oob)//oob_page_size):
        data_page = data[page * data_page_size : (page+1) * data_page_size]
        oob_page = oob[page * oob_page_size : (page+1) * oob_page_size]

        if oob_page[:oob_page_size] == b"\xFF" * oob_page_size:
            continue

        page_ind = int.from_bytes(oob_page[0x6:0x8], "big") & 0x0FFF
        if page_ind in matched:
            print(f"WARN: duplicate page index (Page index: {hex(page_ind)}, OOB offset: {hex(page * 0x10)})")
        else:
            temp_fat = bytearray()
            for block in range(len(oob_page) // 0x10):
                temp_oob = oob_page[block * 0x10 : (block+1) * 0x10]
                if temp_oob[0x8:0xB] != b"\xFF" * 3 or temp_oob[0xC:0x10] != b"\xFF" * 3:
                    temp_fat += data_page[block * 0x200 : (block+1) * 0x200]
            chunk_dicts.append({"fat": temp_fat, "page_ind": page_ind})
        matched.add(page_ind)
        

    
    fat = bytearray()
    for chunk_dict in sorted(chunk_dicts, key=lambda x:x["page_ind"]):
        #print(hex(chunk_dict["page_ind"]))
        fat += chunk_dict["fat"]
            
    with open(output, "wb") as outf:
        outf.write(fat)

if __name__ == "__main__":
    main()
