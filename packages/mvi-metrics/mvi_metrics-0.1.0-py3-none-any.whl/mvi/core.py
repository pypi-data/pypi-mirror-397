from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Tuple, Union

import torch
from torch import nn

LossFn = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]


@dataclass
class MVIResult:
    score: float
    per_batch: List[float]
    n_samples: int


def _safe_mean(xs: List[float]) -> float:
    return float(sum(xs) / max(1, len(xs)))


def score(
    model: nn.Module,
    dataloader: Iterable[Tuple[torch.Tensor, torch.Tensor]],
    loss_fn: LossFn,
    device: Union[str, torch.device] = "cpu",
    max_batches: Optional[int] = None,
    grad_norm_type: float = 2.0,
) -> MVIResult:
    """
    Compute a simple Memory Vulnerability Index (MVI) proxy.

    Higher score = higher vulnerability to forgetting.
    """
    model = model.to(device)
    model.eval()

    per_batch: List[float] = []
    n_samples = 0
    batches_seen = 0

    for x, y in dataloader:
        x = x.to(device)
        y = y.to(device)
        n_samples += int(x.shape[0])

        model.zero_grad(set_to_none=True)

        logits = model(x)
        loss = loss_fn(logits, y)

        grads = torch.autograd.grad(
            loss,
            [p for p in model.parameters() if p.requires_grad],
            retain_graph=False,
            create_graph=False,
            allow_unused=True,
        )

        norms = [g.detach().norm(p=grad_norm_type) for g in grads if g is not None]
        grad_norm = (
            torch.stack(norms).norm(p=grad_norm_type)
            if norms
            else torch.tensor(0.0, device=device)
        )

        batch_mvi = float(grad_norm / (1.0 + grad_norm))
        per_batch.append(batch_mvi)

        batches_seen += 1
        if max_batches is not None and batches_seen >= max_batches:
            break

    return MVIResult(
        score=_safe_mean(per_batch),
        per_batch=per_batch,
        n_samples=n_samples,
    )


def rank_batches(
    model: nn.Module,
    dataloader: Iterable[Tuple[torch.Tensor, torch.Tensor]],
    loss_fn: LossFn,
    k: int = 5,
    device: Union[str, torch.device] = "cpu",
    max_batches: Optional[int] = None,
) -> List[Tuple[int, float]]:
    """
    Return top-k most vulnerable batches.
    """
    res = score(
        model,
        dataloader,
        loss_fn,
        device=device,
        max_batches=max_batches,
    )

    indexed = list(enumerate(res.per_batch))
    indexed.sort(key=lambda t: t[1], reverse=True)
    return indexed[: max(0, k)]


def rank_samples(
    model: nn.Module,
    dataloader: Iterable[Tuple[torch.Tensor, torch.Tensor]],
    loss_fn: LossFn,
    k: int = 20,
    device: Union[str, torch.device] = "cpu",
    max_batches: Optional[int] = None,
) -> List[Tuple[int, float]]:
    """
    Return top-k most vulnerable samples across seen batches.

    MVP implementation (simple, correct):
    - computes per-sample gradient norm proxy
    - higher => more vulnerable
    Output: [(global_sample_index, mvi_score), ...] sorted desc
    """
    model = model.to(device)
    model.eval()

    results: List[Tuple[int, float]] = []
    global_idx = 0
    batches_seen = 0

    for x, y in dataloader:
        x = x.to(device)
        y = y.to(device)

        bs = int(x.shape[0])
        for i in range(bs):
            model.zero_grad(set_to_none=True)

            logits_i = model(x[i : i + 1])
            loss_i = loss_fn(logits_i, y[i : i + 1])

            grads = torch.autograd.grad(
                loss_i,
                [p for p in model.parameters() if p.requires_grad],
                retain_graph=False,
                create_graph=False,
                allow_unused=True,
            )

            norms = [g.detach().norm(p=2.0) for g in grads if g is not None]
            grad_norm = (
                torch.stack(norms).norm(p=2.0)
                if norms
                else torch.tensor(0.0, device=device)
            )

            sample_mvi = float(grad_norm / (1.0 + grad_norm))
            results.append((global_idx, sample_mvi))
            global_idx += 1

        batches_seen += 1
        if max_batches is not None and batches_seen >= max_batches:
            break

    results.sort(key=lambda t: t[1], reverse=True)
    return results[: max(0, k)]









