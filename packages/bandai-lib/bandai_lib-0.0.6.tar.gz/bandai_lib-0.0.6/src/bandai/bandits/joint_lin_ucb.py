from typing import cast

import torch
from jaxtyping import Float
from torch import Tensor

from .protocols import ArmDist, Context, ContextualMAB, Rewards

Mat = Float[Tensor, " A D D"]
Vec = Float[Tensor, " D"]
ArmCtx = Float[Tensor, " A C"]


class JointLinUCB(ContextualMAB):
    """
    JointLinUCB.
    """

    def __init__(
        self,
        arm_ctx: ArmCtx,
        ctx_dim: int,
        exploration_coef: float = 1.0,
    ) -> None:
        self._alpha = exploration_coef

        _, arm_ctx_dim = arm_ctx.shape
        full_ctx_dim = ctx_dim + arm_ctx_dim

        self._arm_ctx = arm_ctx
        self._cov_mat: Mat = torch.eye(full_ctx_dim)
        self._inv_cov: Mat = torch.eye(full_ctx_dim)
        self._bias: Vec = torch.zeros(full_ctx_dim)
        self._estim: Vec = torch.zeros(full_ctx_dim)

    def update(self, arm: int, ctx: Context, rwd: Rewards) -> None:
        batch_size = ctx.shape[0]

        arm_ctx = self._arm_ctx[arm].unsqueeze(0).expand(batch_size, -1)
        ctx = torch.cat([ctx, arm_ctx], dim=1)

        # update A = A + X'X
        self._cov_mat += ctx.T @ ctx

        # update b = b + X'r
        self._bias += ctx.T @ rwd

        # recompute inv(A)
        self._inv_cov = cast(Mat, torch.linalg.inv(self._cov_mat))  # type: ignore

        # update estimate \theta = inv(A) @ b
        self._estim = self._inv_cov @ self._bias

    def predict(self, ctx: Context) -> ArmDist:
        batch_size, _ = ctx.shape
        num_arms, _ = self._arm_ctx.shape

        ctx = torch.cat(
            [  # (B, A, D1 + D2)
                ctx.unsqueeze(1).expand(batch_size, num_arms, -1),  # (B, A, D1)
                self._arm_ctx.unsqueeze(0).expand(batch_size, num_arms, -1),  # (B, A, D2)
            ],
            dim=2,
        )

        # compute mean estimtate x'\theta -> (B, A)
        mean = torch.einsum("bad, d->ba", ctx, self._estim)

        # compute (squared) upper confidence bound x'inv(A)x
        var = torch.einsum("bad, de, bae -> ba", ctx, self._inv_cov, ctx)

        # return final UCB scores
        return mean + self._alpha * var.sqrt()

    @property
    def n_arms(self) -> int:
        return self._arm_ctx.shape[0]

    @property
    def ctx_dim(self) -> int:
        return self._estim.shape[0] - self._arm_ctx.shape[1]
