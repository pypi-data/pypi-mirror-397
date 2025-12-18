from pathlib import Path
from typing import Dict, Any, List, Union

from ..helpers import SlurmScheduler, SGEScheduler, JobResources

class PostProcessingRunner:    
    def __init__(self, root_dir: Union[str, Path], scheduler: str = "slurm"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        
        if scheduler.lower() == "slurm":
            self.scheduler = SlurmScheduler()
        elif scheduler.lower() == "sge":
            self.scheduler = SGEScheduler()
        else:
            raise ValueError("Scheduler must be 'slurm' or 'sge'")

    def _build_cli_args(self, params: Dict[str, Any]) -> List[str]:
        """
        Helper: Converts a python dictionary to a list of CLI flags.
        """
        parts = []
        for k, v in params.items():
            if k == 'n_threads' or k == 'j':
                parts.append(f"-j {v}")
                continue
            
            flag = k.replace("_", "-")
            
            if v is True:
                parts.append(f"--{flag}")
            elif v is False or v is None:
                continue
            else:
                parts.append(f"--{flag}={v}")
                
        return parts

    def run_ambigator(self,
                      input_stream: Union[str, Path],
                      output_stream: Union[str, Path],
                      symmetry: str,
                      env_setup: List[str],
                      resources: Dict[str, Any],
                      params: Dict[str, Any] = None) -> Path:
        print("--- Launching Ambigator ---")
        work_dir = self.root / "ambigator"
        work_dir.mkdir(parents=True, exist_ok=True)
        
        input_stream = Path(input_stream).resolve()
        output_stream = Path(output_stream).resolve()
        params = params or {}
        
        cmd = [
            "ambigator",
            f"-o {output_stream}",
            f"-w {symmetry}"
        ]
        
        cmd.extend(self._build_cli_args(params))
        cmd.append(str(input_stream))
        full_cmd = " ".join(cmd)
        
        n_cpus = params.get('n_threads') or params.get('j') or resources.get('cpus', 1)
        
        res = JobResources(
            name="ambigator",
            time=resources.get('time', '01:00:00'),
            mem=resources.get('mem', '32G'),
            cpus=n_cpus,
            partition=resources.get('partition'),
            account=resources.get('account'),
            log_dir=work_dir
        )
        
        script_path = work_dir / "submit_ambigator.sh"
        self._write_script(script_path, res, full_cmd, env_setup)
        
        jid = self.scheduler.submit(script_path)
        print(f"Ambigator submitted ({jid}). Output: {output_stream}")
        
        return output_stream

    def run_partialator(self,
                        input_stream: Union[str, Path],
                        output_hkl: Union[str, Path],
                        symmetry: str,
                        env_setup: List[str],
                        resources: Dict[str, Any],
                        params: Dict[str, Any] = None) -> Path:
        print("--- Launching Partialator ---")
        work_dir = self.root / "partialator"
        work_dir.mkdir(parents=True, exist_ok=True)
        
        input_stream = Path(input_stream).resolve()
        output_hkl = Path(output_hkl).resolve()
        params = params or {}
        
        cmd = [
            "partialator",
            f"-o {output_hkl}",
            f"-y {symmetry}",
            f"-i {input_stream}"
        ]
        
        cmd.extend(self._build_cli_args(params))
        full_cmd = " ".join(cmd)

        n_cpus = params.get('n_threads') or params.get('j') or resources.get('cpus', 1)

        res = JobResources(
            name="partialator",
            time=resources.get('time', '06:00:00'),
            mem=resources.get('mem', '64G'),
            cpus=n_cpus,
            partition=resources.get('partition'),
            account=resources.get('account'),
            log_dir=work_dir
        )
        
        script_path = work_dir / "submit_partialator.sh"
        self._write_script(script_path, res, full_cmd, env_setup)
        
        jid = self.scheduler.submit(script_path)
        print(f"Partialator submitted ({jid}). Output: {output_hkl}")
        
        return output_hkl

    def _write_script(self, path, res, cmd, env):
        with open(path, 'w') as f:
            f.write("\n".join(self.scheduler.generate_header(res)))
            f.write("\n\n# Environment\n")
            f.write("\n".join(env))
            f.write("\n\n# Execution\n")
            f.write(f"echo 'Starting job in {path.parent}'\n")
            f.write(f"cd {path.parent}\n")
            f.write(f"{cmd}\n")
            f.write("echo 'Job Complete'\n")