from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MlxWorkerSpec:
    gpu_type: str = "NVIDIA-H20"
    gpu_count: int = 1
    cluster: str = "cloudnative-lf"
    queue_name: str = "compute-3291-lf-cloudnative-ai-workspace.public-guarantee"
    resource_type: str = "public-arnold"


def build_mlx_launch_command(script_path: str, spec: MlxWorkerSpec | None = None) -> str:
    spec = spec or MlxWorkerSpec()
    return (
        "NO_COLOR=1 TERM=dumb mlx worker launch "
        f"--resourcetype {spec.resource_type} "
        f"--cluster {spec.cluster} "
        f"--queuename {spec.queue_name} "
        f"--gpu {spec.gpu_count} "
        f"--type {spec.gpu_type} -- "
        f"bash -lc \"python {script_path}\""
    )
