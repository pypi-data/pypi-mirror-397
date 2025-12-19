from joblib import Parallel, delayed
from sklearn.model_selection import KFold
import numpy as np
from typing import Optional

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    MofNCompleteColumn,
)

from .policy import Policy

class AutoPolicy:
    def __init__(
        self,
        predictor,
        label,
        bin_col,
        cost_bad=5.0,
        cost_miss=1.0,
        folds=3,
        iters=40,
        seed=42,
        n_jobs=-1,
        console: Optional[Console] = None,
    ):
        self.p = predictor
        self.label = label
        self.bin_col = bin_col
        self.cb = cost_bad
        self.cm = cost_miss
        self.folds = folds
        self.iters = iters
        self.n_jobs = n_jobs
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.console = console

    def _sample(self):
        ga = self.rng.uniform(0.65, 0.95)
        gd = self.rng.uniform(0.05, ga - 0.05)
        return dict(
            global_approve=ga,
            global_decline=gd,
            sensitivity=self.rng.uniform(0.1, 1.0),
            n_bins=int(self.rng.integers(3, 8)),
        )

    def _fold_cost(self, h, df, tr, va):
        p = Policy(
            self.p,
            self.label,
            self.bin_col,
            **h
        ).fit(df.iloc[tr])
        return p.cost(df.iloc[va], self.cb, self.cm)

    def fit(self, df):
        best, best_cost = None, float("inf")
        kf = KFold(self.folds, shuffle=True, random_state=self.seed)

        progress = Progress(
            SpinnerColumn("dots"),
            TextColumn("[progress.description]{task.description}"),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            TextColumn("best={task.fields[best_cost]:.4f}"),
            TextColumn("last={task.fields[last_cost]:.4f}"),
            console=self.console or Console(),
            transient=False,
        )

        with progress:
            task_id = progress.add_task("autopolicy", total=self.iters, best_cost=best_cost, last_cost=float("nan"))

            for _ in range(self.iters):
                h = self._sample()
                splits = list(kf.split(df))

                costs = Parallel(n_jobs=self.n_jobs, prefer="threads")(
                    delayed(self._fold_cost)(h, df, tr, va)
                    for tr, va in splits
                )

                c = float(np.mean(costs))
                if c < best_cost:
                    best_cost, best = c, h

                progress.update(task_id, advance=1, best_cost=best_cost, last_cost=c)

        return Policy(
            self.p,
            self.label,
            self.bin_col,
            **best
        ).fit(df)
