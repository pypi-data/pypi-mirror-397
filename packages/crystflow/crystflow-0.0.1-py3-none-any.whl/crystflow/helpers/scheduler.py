import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict
from pathlib import Path

@dataclass
class JobResources:
    """Defines resource requirements for a single job."""
    name: str
    time: str
    mem: str
    cpus: int = 1
    partition: Optional[str] = None
    account: Optional[str] = None
    log_dir: Path = Path(".")
    extra_directives: Dict[str, str] = None

class Scheduler(ABC):
    """Abstract base class for job schedulers."""
    @abstractmethod
    def generate_header(self, res: JobResources) -> List[str]:
        pass

    @abstractmethod
    def submit(self, script_path: Path) -> str:
        pass

class SlurmScheduler(Scheduler):
    """SLURM implementation."""
    def generate_header(self, res: JobResources) -> List[str]:
        header = ["#!/bin/bash"]
        directives = {
            "--job-name": res.name,
            "--time": res.time,
            "--mem": res.mem,
            "--ntasks": 1,
            "--cpus-per-task": res.cpus,
            "--output": str(res.log_dir / f"{res.name}_%j.out"),
            "--error": str(res.log_dir / f"{res.name}_%j.err")
        }
        if res.partition: directives["--partition"] = res.partition
        if res.account: directives["--account"] = res.account
        
        for k, v in directives.items():
            header.append(f"#SBATCH {k}={v}")
            
        if res.extra_directives:
            for k, v in res.extra_directives.items():
                header.append(f"#SBATCH {k}={v}")
                
        return header

    def submit(self, script_path: Path) -> str:
        try:
            res = subprocess.run(
                ["sbatch", str(script_path)], 
                capture_output=True, text=True, check=True
            )
            return res.stdout.strip().split()[-1]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"SLURM submission failed: {e.stderr}")

class SGEScheduler(Scheduler):
    """SGE implementation."""
    def generate_header(self, res: JobResources) -> List[str]:
        header = ["#!/bin/bash"]
        header.append(f"#$ -N {res.name}")
        header.append(f"#$ -l h_rt={res.time}")
        header.append(f"#$ -l h_vmem={res.mem}")
        header.append(f"#$ -wd {res.log_dir.resolve()}")
        header.append(f"#$ -o {res.log_dir / f'{res.name}.out'}")
        header.append(f"#$ -e {res.log_dir / f'{res.name}.err'}")
        if res.cpus > 1:
            header.append(f"#$ -pe smp {res.cpus}")
        if res.partition:
            header.append(f"#$ -q {res.partition}")
        return header

    def submit(self, script_path: Path) -> str:
        try:
            res = subprocess.run(
                ["qsub", str(script_path)], 
                capture_output=True, text=True, check=True
            )
            return res.stdout.split()[2]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"SGE submission failed: {e.stderr}")