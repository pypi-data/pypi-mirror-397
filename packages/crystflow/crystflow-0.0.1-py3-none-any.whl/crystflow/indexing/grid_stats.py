import re
import csv
import json
from pathlib import Path
from typing import Dict, Union, Any

STATS_PATTERN = re.compile(
    r"Final: (?P<processed>\d+) images processed, (?P<hits>\d+) hits \(.+?\), (?P<indexable>\d+) indexable"
)

def _parse_run_logs(run_dir: Path) -> Dict[str, int]:
    """
    Scans a directory for ALL log files, extracts stats, and returns the SUM.
    """
    log_files = list(run_dir.glob("*.out")) + \
                list(run_dir.glob("*.err")) + \
                list(run_dir.glob("*.log"))

    totals = {'processed': 0, 'hits': 0, 'indexable': 0}

    for log in log_files:
        try:
            content = log.read_text()
            match = STATS_PATTERN.search(content)
            if match:
                totals['processed'] += int(match.group('processed'))
                totals['hits'] += int(match.group('hits'))
                totals['indexable'] += int(match.group('indexable'))
        except Exception:
            continue
            
    return totals

def _calculate_metrics(raw_stats: Dict[str, int]) -> Dict[str, float]:
    total = raw_stats['processed']
    metrics = {
        'indexing_rate': 0.0,
        'hit_rate': 0.0
    }
    
    if total > 0:
        metrics['indexing_rate'] = round((raw_stats['indexable'] / total) * 100, 2)
        metrics['hit_rate'] = round((raw_stats['hits'] / total) * 100, 2)
        
    return metrics

def analyze_grid_search(project_dir: Union[str, Path], output_csv: str = "grid_summary.csv") -> Dict[str, Any]:
    root = Path(project_dir)
    manifest_path = root / "grid_manifest.json"
    
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}")

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    aggregated_results = []
    
    print(f"Analyzing {len(manifest)} runs in {root}...")

    for entry in manifest:
        run_dir = Path(entry['directory'])
        raw_counts = _parse_run_logs(run_dir)
        metrics = _calculate_metrics(raw_counts)

        row = {
            'run_id': entry['run_id'],
            **metrics,
            **raw_counts,
            **entry['parameters']
        }
        aggregated_results.append(row)

    aggregated_results.sort(key=lambda x: x['indexing_rate'], reverse=True)

    if aggregated_results:
        csv_path = root / output_csv
        headers = list(aggregated_results[0].keys())
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(aggregated_results)
            
        best_run = aggregated_results[0]
        print(f"Best Run: {best_run['run_id']} (Indexing Rate: {best_run['indexing_rate']}%)")
        print(f"Total Processed in Best Run: {best_run['processed']}")
        return best_run
        
    return {}