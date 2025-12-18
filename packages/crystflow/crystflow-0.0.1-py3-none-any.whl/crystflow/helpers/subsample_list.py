from pathlib import Path
import random
from typing import Union, List

def subsample_list(master_list: Path, output_path: Path, n: int):
    with open(master_list, 'r') as f:
        lines = [x.strip() for x in f if x.strip()]
    
    selection = random.sample(lines, n) if len(lines) > n else lines
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write("\n".join(selection))

def split_list(master_list: Union[str, Path], output_dir: Union[str, Path], n_chunks: int) -> List[Path]:
    master_list = Path(master_list)
    output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(master_list, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    total_files = len(lines)
    if total_files == 0:
        raise ValueError(f"Input list {master_list} is empty.")
    chunk_size = (total_files + n_chunks - 1) // n_chunks
    
    created_files = []
    
    for i in range(n_chunks):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size
        chunk_lines = lines[start_idx:end_idx]
        if not chunk_lines:
            break
            
        chunk_path = output_dir / f"chunk_{i:04d}.lst"
        with open(chunk_path, 'w') as f:
            f.write("\n".join(chunk_lines))
        
        created_files.append(chunk_path)
        
    return created_files