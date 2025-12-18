from pathlib import Path
from typing import Union
import shutil

def concat_streams(source_dir: Union[str, Path], output_file: Union[str, Path]):
    source_dir = Path(source_dir)
    output_file = Path(output_file)
    
    stream_files = sorted(source_dir.glob("*.stream"))
    if not stream_files:
        print(f"Warning: No streams found in {source_dir}")
        return

    print(f"Merging {len(stream_files)} streams into {output_file}...")
    
    with open(output_file, 'wb') as outfile:
        for stream in stream_files:
            if stream.stat().st_size == 0:
                continue
            with open(stream, 'rb') as infile:
                shutil.copyfileobj(infile, outfile)