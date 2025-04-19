import sys
import os

possible_start_address_list = [0x0, 0x24, 0x48, 0x50, 0x54, 0x200, 0x2F0] 

def detect_start_address(file_path, possible_start_address_list, magics):
    magic_lens = [len(magic) for magic in magics]
    
    with open(file_path, "rb") as file:
        content = file.read()
        content_len = len(content)
    
    for possible_start_address in possible_start_address_list:
        if content_len < possible_start_address: continue
        for magic, magic_len in zip(magics, magic_lens):
            if content[possible_start_address:possible_start_address+magic_len] == magic:
                return possible_start_address
    
    return None

def main(dfe_dir, possible_start_address_list):
    output_dir = os.path.join(os.path.dirname(dfe_dir), "output_dfe")
    
    input_paths = []
    for root, _, files in os.walk(dfe_dir):
        for file in files:
            input_paths.append(os.path.join(root, file))
    if len(input_paths) == 0: raise ValueError("no file")
    
    print("Looking for the start address...")
    start_address = None
    for input_path in input_paths:
        if not input_path.lower().endswith(".gif"): continue
        start_address = detect_start_address(input_path, possible_start_address_list, [b"GIF89a", b"GIF87a"])
        if start_address != None: break
    
    for input_path in input_paths:
        if not (input_path.lower().endswith(".jpg") or input_path.lower().endswith(".jpeg")): continue
        start_address = detect_start_address(input_path, possible_start_address_list, [b"\xFF\xD8\xFF\xDB", b"\xFF\xD8\xFF\xE0\x00\x10\x4A\x46\x49\x46\x00\x01", b"\xFF\xD8\xFF\xEE", b"\xFF\xD8\xFF\xE1", b"\xFF\xD8\xFF\xE0"])
        if start_address != None: break 
    
    for input_path in input_paths:
        if not input_path.lower().endswith(".mld"): continue
        start_address = detect_start_address(input_path, possible_start_address_list, [b"melo"])
        if start_address != None: break 
    
    for input_path in input_paths:
        if not input_path.lower().endswith(".cfd"): continue
        start_address = detect_start_address(input_path, possible_start_address_list, [b"CFD"])
        if start_address != None: break 
        
    for input_path in input_paths:
        if not input_path.lower().endswith(".swf"): continue
        start_address = detect_start_address(input_path, possible_start_address_list, [b"FWS", b"CWS"])
        if start_address != None: break 
    
    if start_address == None: raise Exception("Failed: The start address could not be found.")
    print(f"Start Address: {hex(start_address)} ({input_path})")
    
    for input_path in input_paths:
        file_name = os.path.basename(input_path)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, file_name)
        
        with open(input_path, "rb") as inf:
            content = inf.read()
                
            if len(content) <= start_address:
                print(f"Ignored: {file_name} (Empty or Symbolic Link)")
                continue
            
            try:
                text = content.decode("utf-8")
                if text[0] == "/":
                    print(f"Ignored: {file_name} (Symbolic Link)")
                    continue
            except:
                pass
            
            
            while True:
                if not os.path.isfile(output_path): break
                output_path = f"{os.path.splitext(output_path)[0]}_{os.path.splitext(output_path)[1]}"
            
            with open(output_path, "wb") as outf:
                outf.write(content[start_address:])
                print(f"Processed: {file_name}")
            
    print(f"Succeeded => {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dfeCutter.py dfe_directory")
    else:
        dfe_dir = sys.argv[1]
        main(dfe_dir, possible_start_address_list)
