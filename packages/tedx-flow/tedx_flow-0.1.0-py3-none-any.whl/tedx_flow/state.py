"""
State management for tedx_flow.

Provides thread-safe state storage with semaphore-based synchronization
for coordinating task dependencies.
"""

from threading import Lock, Semaphore
from typing import Any, Optional


class State:
    """
    Thread-safe state container with semaphore-based synchronization.
    
    Used internally by Context to manage task outputs and coordinate
    dependencies between tasks.
    
    Attributes:
        _value: The stored value
        semaphore: Controls access to value (blocks until value is set)
        _lock: Thread lock for safe value updates
    """
    
    def __init__(self, value: Optional[Any] = None):
        self._value = value
        self.semaphore = Semaphore(0)
        self._lock = Lock()

    def get_value(self) -> Optional[Any]:
        """
        Get the value, blocking until it's available.
        
        This method will block if the value hasn't been set yet,
        making it useful for task dependency coordination.
        
        Returns:
            The stored value
        """
        self.semaphore.acquire()
        output = self._value
        self.semaphore.release()
        return output

    def get_value_with_lock(self) -> Optional[Any]:
        """
        Get the value immediately with lock protection.
        
        Unlike get_value(), this doesn't block waiting for the value.
        Use this for inspection/debugging purposes.
        
        Returns:
            The stored value (may be None if not yet set)
        """
        with self._lock:
            return self._value

    def set_value(self, value: Optional[Any]):
        """
        Set the value and release waiting consumers.
        
        Args:
            value: The value to store
        """
        with self._lock:
            self._value = value
        # Release semaphore to unblock waiting get_value() calls
        self.semaphore.release()

    @classmethod
    def empty(cls) -> "State":
        """Create an empty State instance."""
        return cls(None)
