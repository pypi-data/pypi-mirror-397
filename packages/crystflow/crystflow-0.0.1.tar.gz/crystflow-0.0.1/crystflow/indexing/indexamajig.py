import subprocess
from dataclasses import dataclass, field
from typing import Dict, Any, List, Union, Optional
from pathlib import Path
from ..helpers import split_list, concat_streams

@dataclass
class IndexamajigConfig:

    geometry: Union[str, Path]
    input_list: Union[str, Path]
    output_stream: Union[str, Path]
    cell_file: Optional[Union[str, Path]]
    params: Dict[str, Any] = field(default_factory=dict)

    def to_cli(self) -> str:
        cmd = ["indexamajig", f"-g {self.geometry}", f"-i {self.input_list}", f"-o {self.output_stream}"]
        
        for k, v in self.params.items():
            flag = k.replace("_", "-")
            if v is True: cmd.append(f"--{flag}")
            elif v is False or v is None: continue
            else: cmd.append(f"--{flag}={v}")
        if self.cell_file:
            cmd.append(f"-p {self.cell_file}")
            
        return " ".join(cmd)

class IndexamajigRunner:
    def __init__(self, scheduler_type: str = "slurm"):
        self.scheduler_type = scheduler_type.lower()

    def run_dataset(self, 
                    run_dir: Union[str, Path],
                    master_list: Union[str, Path],
                    geometry: Union[str, Path],
                    cell_file: Optional[Union[str, Path]],
                    optimized_params: Dict[str, Any],
                    env_setup: List[str],
                    resources: Dict[str, Any],
                    n_jobs: int = 100,
                    dry_run: bool = False) -> Path:

        run_dir = Path(run_dir)
        list_dir = run_dir / "lists"
        stream_dir = run_dir / "streams"
        log_dir = run_dir / "logs"
        
        for d in [list_dir, stream_dir, log_dir]:
            d.mkdir(parents=True, exist_ok=True)

        print(f"Splitting inputs into {n_jobs} chunks...")
        chunks = split_list(master_list, list_dir, n_jobs)

        print(f"Submitting {len(chunks)} jobs...")
        job_ids = []

        for i, chunk in enumerate(chunks):
            job_name = f"idx_{i:04d}"
            chunk_stream = stream_dir / f"{job_name}.stream"
            
            cfg = IndexamajigConfig(
                geometry=geometry,
                input_list=chunk,
                output_stream=chunk_stream,
                cell_file=cell_file,
                params=optimized_params
            )
            
            script_path = run_dir / f"submit_{i:04d}.sh"
            self._write_script(
                path=script_path,
                name=job_name,
                cmd=cfg.to_cli(),
                env=env_setup,
                res=resources,
                log_dir=log_dir
            )

            if not dry_run:
                jid = self._submit_to_scheduler(script_path)
                job_ids.append(jid)

        if not dry_run:
            print(f"Submitted {len(job_ids)} jobs.")
        
        return stream_dir

    def finalize(self, stream_dir: Path, output_filename: str = "final.stream"):
        stream_dir = Path(stream_dir)
        output_path = stream_dir.parent / output_filename
        concat_streams(stream_dir, output_path)
        return output_path

    def _write_script(self, path, name, cmd, env, res, log_dir):
        """Internal script generator."""
        lines = ["#!/bin/bash"]
        if self.scheduler_type == "slurm":
            lines.append(f"#SBATCH --job-name={name}")
            lines.append(f"#SBATCH --output={log_dir}/{name}.out")
            lines.append(f"#SBATCH --error={log_dir}/{name}.err")
            lines.append(f"#SBATCH --time={res.get('time', '01:00:00')}")
            lines.append(f"#SBATCH --mem={res.get('mem', '4G')}")
            lines.append(f"#SBATCH --cpus-per-task={res.get('cpus', 1)}")
            if 'partition' in res: lines.append(f"#SBATCH --partition={res['partition']}")
        elif self.scheduler_type == "sge":
            lines.append(f"#$ -N {name}")
            lines.append(f"#$ -o {log_dir}/{name}.out")
            lines.append(f"#$ -e {log_dir}/{name}.err")
        
        lines.append("\n# Environment")
        lines.extend(env)
        
        lines.append("\n# Execution")
        lines.append(cmd)
        
        with open(path, 'w') as f:
            f.write("\n".join(lines))

    def _submit_to_scheduler(self, script_path):
        if self.scheduler_type == "slurm":
            cmd = ["sbatch", str(script_path)]
        else:
            cmd = ["qsub", str(script_path)]
            
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return r.stdout.strip().split()[-1]