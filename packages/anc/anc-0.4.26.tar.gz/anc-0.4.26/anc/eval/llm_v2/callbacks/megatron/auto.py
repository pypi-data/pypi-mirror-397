import os
import sys
import json
import time
import requests
import threading
from loguru import logger

from megatron.training.checkpointing import (
    get_checkpoint_name,
    get_checkpoint_tracker_filename,
    isfile,
    read_metadata,
)

from megatron.a7n.utils import rank_zero_info, rank_zero_only
from megatron.a7n.callbacks.callbacks import Callback
from megatron.a7n.base_trainer import BaseTrainer


from ...triggers.workflow import AutoEvaluationWorkflowTrigger


class AutoEvaluationCallback(Callback):
    """
    Callback for triggering evaluation pipeline at specified training step intervals.

    This callback tracks training progress and triggers evaluation pipeline
    every stride_steps_eval steps. When the interval is reached, it evaluates
    the current checkpoint.

    Args:
        args: Arguments object containing stride_steps_eval and other configuration

    Example usage:
        # If stride_steps_eval = 100
        # Training steps: 50, 100, 150, 200, 250, 300...
        # 
        # Evaluation will be triggered:
        # - At step 100 -> evaluate current checkpoint
        # - At step 200 -> evaluate current checkpoint  
        # - At step 300 -> evaluate current checkpoint
        # 
        # This provides regular evaluation intervals based on training progress.

    Configuration:
        args.stride_steps_eval (int): Interval for step-based evaluation
            - If None or 0: Only evaluate at training end
            - If > 0: Evaluate every N steps (using the current checkpoint)
    """

    def __init__(self, args, target_callback_type, code_info=None):
        super().__init__()
        self.workflow_trigger = AutoEvaluationWorkflowTrigger(args, code_info=code_info)
        self.stride_steps_eval = getattr(args, 'stride_steps_eval', None)
        self.checkpoint_list = []
        self.checkpoint_count = 0
        self.evaluated_checkpoints = set()
        self.target_callback_type = target_callback_type

        rank_zero_info(
            f"AutoEvaluationCallback v2 initialized with stride_steps_eval={self.stride_steps_eval}")
        if self.stride_steps_eval and self.stride_steps_eval > 0:
            rank_zero_info(
                f"Will evaluate every {self.stride_steps_eval} steps using the current checkpoint")
            rank_zero_info(
                f"Evaluation trigger: when global steps % {self.stride_steps_eval} == 0")
            rank_zero_info(f"Final checkpoint will always be evaluated regardless of stride")
        else:
            rank_zero_info("Evaluation will only be triggered at training end")
        
        self.hooks_take_effect = ["on_save_checkpoint", "on_train_end"]

    def on_save_checkpoint(self, trainer: BaseTrainer):
        if self.stride_steps_eval is None or self.stride_steps_eval == 0:
            return

        if last_ckpt_path := self._get_last_ckpt_path(trainer):
            if last_ckpt_path in self.checkpoint_list:
                # rank_zero_info(f"Checkpoint already processed, skipping: {last_ckpt_path}")
                return
            self.checkpoint_list.append(last_ckpt_path)
            self.checkpoint_count += 1
            if trainer.iteration % self.stride_steps_eval == 0:
                target_ckpt = last_ckpt_path
                rank_zero_info(
                    f"Scheduling evaluation for current checkpoint (#{self.checkpoint_count}): {target_ckpt}"
                )
                self.evaluated_checkpoints.add(last_ckpt_path)
                self._schedule_evaluation_when_checkpoint_exists(trainer, target_ckpt)

    def _get_last_ckpt_path(self, trainer: BaseTrainer):
        save_path = trainer.args.save
        last_ckpt_path = None
        if save_path is not None:
            tracker_filename = get_checkpoint_tracker_filename(save_path)
            if isfile(tracker_filename):
                iteration, release = read_metadata(tracker_filename)
                last_ckpt_path = get_checkpoint_name(
                    save_path,
                    iteration,
                    release=False,
                    pipeline_parallel=None,
                    tensor_rank=None,
                    pipeline_rank=None,
                    expert_parallel=None,
                    expert_rank=None,
                    return_base_dir=True
                )
                if not os.path.exists(last_ckpt_path):
                    rank_zero_info(f"last ckpt path not found: {last_ckpt_path}")
                    return None
        return last_ckpt_path
    
    @rank_zero_only
    def _schedule_evaluation_when_checkpoint_exists(self, trainer: BaseTrainer, checkpoint_path: str):
        def check_and_evaluate():
            max_wait_time = 600
            check_interval = 5
            waited_time = 0

            rank_zero_info(f"Background thread: Waiting for checkpoint to exist: {checkpoint_path}")

            while waited_time < max_wait_time:
                try:
                    checkpoint_exists = False

                    if os.path.isdir(checkpoint_path):
                        checkpoint_exists = True

                    if checkpoint_exists:
                        rank_zero_info(
                            f"Background thread: Checkpoint verified, triggering evaluation: {checkpoint_path}")
                        self._trigger_evaluation(trainer, checkpoint_path)
                        return
                    else:
                        rank_zero_info(
                            f"Background thread: Checked: {checkpoint_path}, {checkpoint_path}.ckpt, directory {checkpoint_path}")

                except Exception as e:
                    rank_zero_info(f"Background thread: Error checking checkpoint: {e}")

                time.sleep(check_interval)
                waited_time += check_interval

            rank_zero_info(
                f"Eval warning: timeout waiting for checkpoint, attempting evaluation anyway: {checkpoint_path}"
            )
            self._trigger_evaluation(trainer, checkpoint_path)

        check_thread = threading.Thread(target=check_and_evaluate, daemon=True)
        check_thread.start()
        rank_zero_info(f"Started background thread to monitor checkpoint: {checkpoint_path}")
    
    @rank_zero_only
    def _trigger_evaluation(self, trainer: BaseTrainer, checkpoint_path: str):
        try:
            tflops_monitor = next(
                (cb for cb in trainer.callbacks if isinstance(
                    cb, self.target_callback_type)),  
                None
            )

            metrics = {"avg_tflops": 0.0, "avg_mfu": 0.0, "steps": 0}
            if tflops_monitor:
                metrics = tflops_monitor.get_performance_metrics()
                rank_zero_info(
                    f"Performance metrics for checkpoint {checkpoint_path}: "
                    f"Avg TFLOPS={metrics['avg_tflops']:.2f}, "
                    f"Avg MFU={metrics['avg_mfu']:.4f}, "
                    f"Steps={metrics['steps']}"
                )

            response = self.workflow_trigger.trigger(
                checkpoint_path,
                metrics.get('avg_tflops', 0.0),
                metrics.get('avg_mfu', 0.0),
                metrics.get('steps', 0)
            )
            rank_zero_info(
                f"Evaluation triggered successfully for {checkpoint_path}. Response: {response}"
            )

        except Exception as e:
            rank_zero_info(f"Failed to trigger evaluation for {checkpoint_path}: {e}")

    def on_train_end(self, trainer: BaseTrainer):
        """Get the final checkpoint path at the end of training"""

        last_ckpt = self._get_last_ckpt_path(trainer)

        if not last_ckpt:
            rank_zero_info("Warning: last_model_path is empty. No checkpoint was saved.")
            return

        rank_zero_info(f"Final checkpoint path: {last_ckpt}")

        tflops_monitor = next(
            (cb for cb in trainer.callbacks if isinstance(cb, self.target_callback_type)),
            None
        )
        metrics = None

        if tflops_monitor:
            metrics = tflops_monitor.get_performance_metrics()
            avg_tflops = metrics['avg_tflops']
            avg_mfu = metrics['avg_mfu']
            steps = metrics['steps']
            rank_zero_info(
                f"Performance metrics: Avg TFLOPS={avg_tflops:.2f}, Avg MFU={avg_mfu:.4f}, Steps={steps}")

        if last_ckpt not in self.evaluated_checkpoints:
            rank_zero_info(
                f"Final checkpoint has not been evaluated yet, scheduling evaluation: {last_ckpt}")
            self.evaluated_checkpoints.add(last_ckpt)
            self._schedule_evaluation_when_checkpoint_exists(trainer, last_ckpt)
        else:
            rank_zero_info(f"Final checkpoint has already been scheduled for evaluation, skipping: {last_ckpt}")

    def get_checkpoint_list(self):
        return self.checkpoint_list.copy()

    def get_checkpoint_count(self):
        return self.checkpoint_count
