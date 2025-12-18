from typing import Any

from dojo_sdk_client.dojo_eval_client import EvaluationResult
import requests

from dojo_sdk_client.base_dojo_client import BaseDojoClient


class DojoBenchClient(BaseDojoClient):
    def submit_benchmark_score(
        self,
        job_id: str,
        score: float,
        bench_name: str,
        bench_version: str,
        model_name: str,
        provider: str,
        score_config: dict[str, Any],
    ) -> float:
        response = requests.post(
            f"{self.http_endpoint}/benchmarks/score",
            json={
                "job_id": job_id,
                "score": score,
                "score_config": score_config,
                "bench_name": bench_name,
                "bench_version": bench_version,
                "model_name": model_name,
                "model_provider": provider,
            },
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    def get_job_tasks(self, job_id: str) -> list[str]:
        response = requests.get(
            f"{self.http_endpoint}/benchmarks/{job_id}/tasks",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

