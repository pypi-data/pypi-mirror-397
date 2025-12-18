from pathlib import Path
from typing import Union

def expand_source_list(
    source_list: Union[str, Path],
    output_list: Union[str, Path],
    n_frames: int,
    event_pattern: str = "//entry_{i}",
    start_index: int = 0,
    include_index_column: bool = True  # <--- NEW DEFAULT
) -> Path:
    source_list = Path(source_list).resolve()
    output_list = Path(output_list).resolve()
    
    if not source_list.exists():
        raise FileNotFoundError(f"Source list not found: {source_list}")

    print(f"Expanding file list from: {source_list}")
    print(f"Settings: {n_frames} frames/file, pattern='{event_pattern}', 3rd_col={include_index_column}")

    output_list.parent.mkdir(parents=True, exist_ok=True)
    
    total_events = 0
    
    try:
        with open(source_list, 'r') as src, open(output_list, 'w') as dst:
            for line in src:
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue
                
                filepath = cleaned_line.split()[0]
    
                for i in range(start_index, start_index + n_frames):
                    tag = event_pattern.format(i=i)
                    out_line = f"{filepath} {tag}"

                    if include_index_column:
                        out_line += f" {i}"
                    
                    dst.write(out_line + "\n")
                    total_events += 1
                    
        print(f"Expansion complete.")
        print(f"-> Wrote {total_events} events to: {output_list}")
        
    except IOError as e:
        print(f"Error writing list file: {e}")
        raise

    return output_list