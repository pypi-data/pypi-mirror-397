"""
Training callbacks for AI Trainer Bot.
"""

from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
import torch
import time


class Callback(ABC):
    """
    Base callback class.
    """

    def on_train_begin(self, logs: Optional[Dict[str, Any]] = None):
        """Called at the beginning of training."""
        pass

    def on_train_end(self, logs: Optional[Dict[str, Any]] = None):
        """Called at the end of training."""
        pass

    def on_epoch_begin(self, epoch: int, logs: Optional[Dict[str, Any]] = None):
        """Called at the beginning of each epoch."""
        pass

    def on_epoch_end(self, epoch: int, logs: Optional[Dict[str, Any]] = None):
        """Called at the end of each epoch."""
        pass

    def on_batch_begin(self, batch: int, logs: Optional[Dict[str, Any]] = None):
        """Called at the beginning of each batch."""
        pass

    def on_batch_end(self, batch: int, logs: Optional[Dict[str, Any]] = None):
        """Called at the end of each batch."""
        pass


class CallbackList:
    """
    List of callbacks.
    """

    def __init__(self, callbacks: Optional[list] = None):
        self.callbacks = callbacks or []

    def append(self, callback: Callback):
        """Add a callback."""
        self.callbacks.append(callback)

    def on_train_begin(self, logs=None):
        for callback in self.callbacks:
            callback.on_train_begin(logs)

    def on_train_end(self, logs=None):
        for callback in self.callbacks:
            callback.on_train_end(logs)

    def on_epoch_begin(self, epoch, logs=None):
        for callback in self.callbacks:
            callback.on_epoch_begin(epoch, logs)

    def on_epoch_end(self, epoch, logs=None):
        for callback in self.callbacks:
            callback.on_epoch_end(epoch, logs)

    def on_batch_begin(self, batch, logs=None):
        for callback in self.callbacks:
            callback.on_batch_begin(batch, logs)

    def on_batch_end(self, batch, logs=None):
        for callback in self.callbacks:
            callback.on_batch_end(batch, logs)


class ModelCheckpoint(Callback):
    """
    Save model checkpoints.
    """

    def __init__(self, filepath: str, monitor: str = 'val_loss',
                 save_best_only: bool = True, mode: str = 'min'):
        self.filepath = filepath
        self.monitor = monitor
        self.save_best_only = save_best_only
        self.mode = mode
        self.best_value = float('inf') if mode == 'min' else float('-inf')
        self.best_score = self.best_value

    def on_epoch_end(self, epoch: int, logs: Optional[Dict[str, Any]] = None, model=None):
        logs = logs or {}
        current_value = logs.get(self.monitor)

        if current_value is None:
            return

        should_save = False
        if self.mode == 'min' and current_value < self.best_value:
            should_save = True
        elif self.mode == 'max' and current_value > self.best_value:
            should_save = True

        if should_save or not self.save_best_only:
            self.best_value = current_value
            self.best_score = current_value
            # Save model
            torch.save(model.state_dict(), self.filepath)


class EarlyStopping(Callback):
    """
    Early stopping callback.
    """

    def __init__(self, monitor: str = 'val_loss', patience: int = 10,
                 mode: str = 'min', restore_best_weights: bool = False):
        self.monitor = monitor
        self.patience = patience
        self.mode = mode
        self.restore_best_weights = restore_best_weights
        self.best_value = float('inf') if mode == 'min' else float('-inf')
        self.wait = 0
        self.stopped_epoch = 0
        self.best_weights = None
        # Aliases for tests
        self.stopped = False

    @property
    def best_score(self):
        return self.best_value

    @best_score.setter
    def best_score(self, value):
        self.best_value = value

    @property
    def counter(self):
        return self.wait

    @counter.setter
    def counter(self, value):
        self.wait = value

    def on_epoch_end(self, epoch: int, logs: Optional[Dict[str, Any]] = None):
        logs = logs or {}
        current_value = logs.get(self.monitor)

        if current_value is None:
            return

        if self.mode == 'min' and current_value < self.best_value:
            self.best_value = current_value
            self.best_score = current_value
            self.wait = 0
            self.counter = 0
            if self.restore_best_weights:
                # self.best_weights = model.get_weights()
                pass
        elif self.mode == 'max' and current_value > self.best_value:
            self.best_value = current_value
            self.best_score = current_value
            self.wait = 0
            self.counter = 0
            if self.restore_best_weights:
                # self.best_weights = model.get_weights()
                pass
        else:
            self.wait += 1
            self.counter = self.wait

        if self.wait >= self.patience:
            self.stopped_epoch = epoch
            self.stopped = True
            # Stop training
            # self.model.stop_training = True


class LearningRateScheduler(Callback):
    """
    Learning rate scheduler callback.
    """

    def __init__(self, scheduler):
        self.scheduler = scheduler

    def on_epoch_end(self, epoch: int, logs: Optional[Dict[str, Any]] = None):
        self.scheduler.step()


class TensorBoardCallback(Callback):
    """
    TensorBoard logging callback.
    """

    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        # self.writer = SummaryWriter(log_dir)

    def on_epoch_end(self, epoch: int, logs: Optional[Dict[str, Any]] = None):
        logs = logs or {}
        # Log metrics to TensorBoard
        # for key, value in logs.items():
        #     self.writer.add_scalar(key, value, epoch)


class ProgressCallback(Callback):
    """
    Progress reporting callback.
    """

    def __init__(self, verbose: int = 1):
        self.verbose = verbose
        self.start_time = None

    def on_train_begin(self, logs=None):
        self.start_time = time.time()
        if self.verbose > 0:
            print("Training started...")

    def on_epoch_end(self, epoch: int, logs: Optional[Dict[str, Any]] = None):
        logs = logs or {}
        if self.verbose > 0:
            elapsed = time.time() - self.start_time
            loss = logs.get('loss', 'N/A')
            val_loss = logs.get('val_loss', 'N/A')
            print(f"Epoch {epoch}: loss={loss}, val_loss={val_loss}, "
                  f"elapsed={elapsed:.2f}s")

    def on_train_end(self, logs=None):
        if self.verbose > 0:
            total_time = time.time() - self.start_time
            print(f"Training completed in {total_time:.2f} seconds")