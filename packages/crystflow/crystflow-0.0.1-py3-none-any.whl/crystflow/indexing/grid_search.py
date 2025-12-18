import itertools
import shutil
from pathlib import Path
from typing import List, Dict, Union, Any, Optional
from ..helpers import Scheduler, SlurmScheduler, SGEScheduler, JobResources, subsample_list, split_list
from .indexamajig import IndexamajigConfig

class IndexingGridSearch:
    def __init__(self, base_work_dir: Union[str, Path], scheduler: str = "slurm"):
        self.base_dir = Path(base_work_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        if scheduler.lower() == "slurm":
            self.scheduler_handler = SlurmScheduler()
        elif scheduler.lower() == "sge":
            self.scheduler_handler = SGEScheduler()
        else:
            raise ValueError("Scheduler must be 'slurm' or 'sge'")

    def launch(self,
               master_list: Union[str, Path],
               geometry_file: Union[str, Path],
               cell_file: Optional[Union[str, Path]],
               base_params: Dict[str, Any],
               grid_params: Dict[str, List[Any]],
               env_preamble: List[str],
               n_subsample: int = 1000,
               n_jobs_per_grid: int = 1,
               job_resources: Dict[str, Any] = None,
               dry_run: bool = False) -> List[Dict[str, Any]]:
        
        master_list = Path(master_list).resolve()
        geometry_file = Path(geometry_file).resolve()
        resolved_cell = Path(cell_file).resolve() if cell_file else None

        subsample_master = self.base_dir / "subsample_master.lst"
        subsample_list(master_list, subsample_master, n_subsample)

        list_dir = self.base_dir / "lists"
        chunk_files = split_list(subsample_master, list_dir, n_jobs_per_grid)
        
        local_geom = self.base_dir / "geometry.geom"
        shutil.copy(geometry_file, local_geom)

        keys = list(grid_params.keys())
        combinations = list(itertools.product(*grid_params.values()))
        
        results = []
        default_res = {'time': '01:00:00', 'mem': '4G', 'cpus': 4}
        if job_resources:
            default_res.update(job_resources)

        print(f"Grid: {len(combinations)} parameter sets x {n_jobs_per_grid} jobs each = {len(combinations)*n_jobs_per_grid} total jobs.")

        for i, values in enumerate(combinations):
            current_grid_vals = dict(zip(keys, values))
            run_params = {**base_params, **current_grid_vals}
            
            run_id = f"run_{i:03d}"
            run_dir = self.base_dir / "runs" / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            
            run_job_ids = []

            for j, chunk_path in enumerate(chunk_files):
                
                part_name = f"part_{j:02d}"
                stream_file = run_dir / f"{part_name}.stream"
                idx_conf = IndexamajigConfig(
                    geometry=local_geom.resolve(),
                    input_list=chunk_path.resolve(),
                    output_stream=stream_file.resolve(),
                    cell_file=resolved_cell,
                    params=run_params
                )
                
                n_cpus = run_params.get('n_threads') or run_params.get('j') or default_res['cpus']
                
                res = JobResources(
                    name=f"gs_{i:03d}_{j:02d}",
                    time=default_res['time'],
                    mem=default_res['mem'],
                    cpus=n_cpus,
                    partition=default_res.get('partition'),
                    account=default_res.get('account'),
                    log_dir=run_dir 
                )

                script_path = run_dir / f"submit_{j:02d}.sh"
                self._write_script(script_path, res, idx_conf, env_preamble)
                
                if not dry_run:
                    jid = self.scheduler_handler.submit(script_path)
                    run_job_ids.append(jid)
                else:
                    run_job_ids.append("DRY_RUN")

            results.append({
                "run_id": run_id,
                "directory": str(run_dir),
                "parameters": run_params,
                "job_ids": run_job_ids # List of IDs
            })

        return results

    def _write_script(self, path, res, config, preamble):
        with open(path, 'w') as f:
            f.write("\n".join(self.scheduler_handler.generate_header(res)))
            f.write("\n\n# Environment\n")
            for line in preamble: f.write(f"{line}\n")
            f.write(f"\n# Execution\ncd {path.parent}\n")
            f.write(config.to_cli())
            f.write("\n")