from pathlib import Path
from typing import List, Dict, Any, Union

from .indexamajig import IndexamajigConfig
from ..helpers import SlurmScheduler, SGEScheduler, JobResources, split_list

class DetectorRefiner:
    def __init__(self, root_dir: Union[str, Path], scheduler: str = "slurm"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        
        if scheduler.lower() == "slurm":
            self.scheduler = SlurmScheduler()
        elif scheduler.lower() == "sge":
            self.scheduler = SGEScheduler()
        else:
            raise ValueError("Scheduler must be 'slurm' or 'sge'")

    def generate_mille_data(self,
                            master_list: Union[str, Path],
                            geometry: Union[str, Path],
                            cell_file: Union[str, Path],
                            best_params: Dict[str, Any],
                            env_setup: List[str],
                            resources: Dict[str, Any],
                            n_jobs: int = 10,
                            max_mille_level: int = 2) -> Path:
        """
        Step 1: Runs indexamajig to generate Millepede binary files (*.bin).
        """
        print("--- Refinement Step 1: Generating Calibration Data ---")
        work_dir = self.root / "refinement_data"
        lists_dir = work_dir / "lists"
        logs_dir = work_dir / "logs"
        bin_dir = work_dir / "mille_bins"
        
        for d in [lists_dir, logs_dir, bin_dir]:
            d.mkdir(parents=True, exist_ok=True)
        chunks = split_list(master_list, lists_dir, n_jobs)
        
        job_ids = []
        
        for i, chunk in enumerate(chunks):
            job_name = f"mille_gen_{i:03d}"
            
            trash_stream = work_dir / f"trash_{i:03d}.stream"
            mille_file = bin_dir / f"mille_{i:03d}.bin"
            
            run_params = best_params.copy()
            run_params['mille'] = True
            run_params['mille_file'] = str(mille_file)
            run_params['max_mille_level'] = max_mille_level
            run_params['check_peaks'] = True 

            cfg = IndexamajigConfig(
                geometry=Path(geometry).resolve(),
                input_list=chunk,
                output_stream=trash_stream,
                cell_file=Path(cell_file).resolve(),
                params=run_params
            )
            
            res = JobResources(
                name=job_name,
                time=resources.get('time', '01:00:00'),
                mem=resources.get('mem', '8G'),
                cpus=resources.get('cpus', 4),
                partition=resources.get('partition'),
                account=resources.get('account'),
                log_dir=logs_dir
            )

            script_path = work_dir / f"submit_{i:03d}.sh"
            with open(script_path, 'w') as f:
                f.write("\n".join(self.scheduler.generate_header(res)))
                f.write("\n\n# Environment\n")
                f.write("\n".join(env_setup))
                f.write("\n\n# Execution\n")
                f.write(cfg.to_cli())
                f.write("\n")

            jid = self.scheduler.submit(script_path)
            job_ids.append(jid)

        print(f"Submitted {len(job_ids)} jobs. Output bins will be in: {bin_dir}")
        return bin_dir

    def run_alignment(self,
                      geometry_in: Union[str, Path],
                      mille_dir: Union[str, Path],
                      output_geometry: str,
                      level: int,
                      env_setup: List[str],
                      resources: Dict[str, Any],
                      flags: Dict[str, bool] = None) -> Path:
        
        print("--- Refinement Step 2: Calculating Alignment ---")
        work_dir = self.root / "alignment_run"
        work_dir.mkdir(parents=True, exist_ok=True)
        
        geo_out = work_dir / output_geometry
        geo_in = Path(geometry_in).resolve()
        mille_dir = Path(mille_dir).resolve()
        cmd = [
            "align_detector",
            f"-g {geo_in}",
            f"-o {geo_out}",
            f"-l {level}"
        ]
        
        if flags:
            if flags.get('camera_length'): cmd.append("--camera-length")
            if flags.get('out_of_plane'): cmd.append("--out-of-plane")
            if flags.get('out_of_plane_tilts'): cmd.append("--out-of-plane-tilts")
            if flags.get('panel_totals'): cmd.append("--panel-totals")

        cmd.append(f"{mille_dir}/*.bin")
        
        full_cmd = " ".join(cmd)

        res = JobResources(
            name="align_det",
            time=resources.get('time', '00:30:00'),
            mem=resources.get('mem', '32G'),
            cpus=1,
            partition=resources.get('partition'),
            account=resources.get('account'),
            log_dir=work_dir
        )

        script_path = work_dir / "submit_align.sh"
        with open(script_path, 'w') as f:
            f.write("\n".join(self.scheduler.generate_header(res)))
            f.write("\n\n# Environment\n")
            f.write("\n".join(env_setup))
            f.write("\n\n# Execution\n")
            f.write(f"echo 'Starting alignment...'\n")
            f.write(f"{full_cmd}\n")
            f.write(f"echo 'Done. New geometry at {geo_out}'\n")

        jid = self.scheduler.submit(script_path)
        print(f"Alignment job submitted: {jid}")
        print(f"Watch for output at: {geo_out}")
        
        return geo_out