"""Module for converting binary DIMACS graph files (.col.b) to ASCII format (.col)."""

from os import path, listdir, remove
from constants import EVAL_INPUT_DIR

INPUT_FILES: list[str] = [
    "flat300_20_0.col.b",
    "flat300_26_0.col.b",
    "flat300_28_0.col.b",
    "flat1000_50_0.col.b",
    "flat1000_60_0.col.b",
    "flat1000_76_0.col.b",
]

def convert_bin_to_ascii(bin_path: str, ascii_path: str) -> None:
    """Converts a binary .col.b DIMACS graph to textual .col format.
    
    Returns:
        None
    """
    with open(bin_path, "rb") as f_in:
        preamble_len_str: bytes = b""
        while True:
            char: bytes = f_in.read(1)
            if char == b"\n" or not char:
                break
            preamble_len_str += char
            
        preamble_length: int = int(preamble_len_str.strip())
        
        preamble: str = f_in.read(preamble_length).decode("utf-8", errors="ignore")
        num_nodes: int = 0
        
        for line in preamble.splitlines():
            parts: list[str] = line.strip().split()
            if parts and parts[0] == "p" and len(parts) >= 3:
                num_nodes = int(parts[2])
                break
                
        if num_nodes == 0:
            raise ValueError("Preambula ne sadrži ispravnu 'p' liniju.")
            
        with open(ascii_path, "w", encoding="utf-8") as f_out:
            f_out.write(preamble)
            if not preamble.endswith("\n"):
                f_out.write("\n")
                
            masks: list[int] = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
            
            for i in range(num_nodes):
                bytes_to_read: int = (i + 8) // 8
                row_data: bytes = f_in.read(bytes_to_read)
                
                if not row_data:
                    break
                    
                for j in range(i + 1):
                    bit: int = 7 - (j & 0x00000007)
                    byte_idx: int = j >> 3
                    
                    mask: int = masks[bit]
                    if (row_data[byte_idx] & mask) == mask:
                        f_out.write(f"{i + 1} {j + 1}\n")

def convert_bin_files() -> None:
    """Converts all binary DIMACS graph files in INPUT_FILES to ASCII format.
    
    Returns:
        None
    """
    for input_file in INPUT_FILES:
        bin_path: str = path.join(EVAL_INPUT_DIR, input_file)
        ascii_path: str = path.join(EVAL_INPUT_DIR, input_file.replace(".col.b", ".col"))
        
        try:
            convert_bin_to_ascii(bin_path, ascii_path)
            print(f"Successfully converted {bin_path} to {ascii_path}.")
        except Exception as e:
            print(f"Error converting {bin_path}: {e}")

def preprocess_ascii_file(ascii_path: str) -> None:
    """Preprocesses the ASCII DIMACS graph file to ensure it has the correct format.
    
    Args:
        ascii_path (str): Path to the ASCII DIMACS graph file.
        
    Returns:
        None
    """
    if not path.exists(ascii_path):
        raise FileNotFoundError(f"File {ascii_path} does not exist.")

    lines: list[str] = []
    with open(ascii_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    lines = [line.strip() for line in lines if line.strip()]
    lines = [line for line in lines if not line.startswith("c")]
    lines[0] = lines[0].replace("p edge ", "")
    lines = [line.removeprefix("e ") for line in lines]

    output_file: str = ascii_path.replace(".col", ".txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def preprocess_ascii_files() -> None:
    """Preprocesses all ASCII DIMACS graph files to ensure they have the correct format.
    
    Returns:
        None
    """
    for input_file in listdir(EVAL_INPUT_DIR):
        ascii_path: str = path.join(EVAL_INPUT_DIR, input_file)
        
        try:
            preprocess_ascii_file(ascii_path)
            print(f"Successfully preprocessed {ascii_path}.")
        except Exception as e:
            print(f"Error preprocessing {ascii_path}: {e}")

def remove_ascii_files() -> None:
    """Removes all ASCII DIMACS graph files.
    
    Returns:
        None
    """
    for input_file in listdir(EVAL_INPUT_DIR):
        ascii_path: str = path.join(EVAL_INPUT_DIR, input_file)
        if not (ascii_path.endswith(".col") or ascii_path.endswith(".col.b")):
            continue

        try:
            if path.exists(ascii_path):
                remove(ascii_path)
                print(f"Successfully removed {ascii_path}.")
            else:
                print(f"File {ascii_path} does not exist.")
        except Exception as e:
            print(f"Error removing {ascii_path}: {e}")

def main() -> None:
    """Main function to convert a binary DIMACS graph file to ASCII format.
    
    Returns:
        None
    """
    print("Starting conversion of binary DIMACS graph files to ASCII format...")
    convert_bin_files()
    
    print("\nStarting preprocessing of ASCII DIMACS graph files...")
    preprocess_ascii_files()
    
    print("\nStarting removal of ASCII DIMACS graph files...")
    remove_ascii_files()

if __name__ == "__main__":
    main()