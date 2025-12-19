"""
Context management for tedx_flow.

Provides a shared context for passing data between tasks in a flow.
"""

from queue import Queue
from typing import Any, Dict, Optional

from .state import State


class Context:
    """
    Shared context for task communication within a flow.
    
    Context stores task outputs and provides a mechanism for tasks
    to access results from other tasks. It also supports streaming
    for real-time output delivery.
    
    Example:
        ctx = Context()
        ctx.set("task_a", "Hello")
        value = ctx.get("task_a")  # "Hello"
    """
    
    stream: Optional[Queue] = None

    def __init__(self):
        self.states: Dict[str, State] = {}

    def get(self, key: str) -> Any:
        """
        Get a value from context by key.
        
        This method blocks until the value is available, making it
        safe to use for task dependencies.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The stored value
            
        Raises:
            Exception: If key doesn't exist in context
        """
        if key not in self.states:
            raise Exception(f"Key {key} not found in context")

        state = self.states[key]
        return state.get_value()

    def set(self, key: str, message: Any):
        """
        Set a value in context.
        
        Args:
            key: The key to store under
            message: The value to store
        """
        if key not in self.states:
            state = State()
            state.set_value(message)
            self.states[key] = state
        else:
            state = self.states[key]
            state.set_value(message)

    def set_state(self, key: str, state: State):
        """
        Set a State object directly.
        
        Args:
            key: The key to store under
            state: The State object
        """
        self.states[key] = state

    def set_stream(self, stream: Queue):
        """
        Set the stream queue for real-time output.
        
        Args:
            stream: Queue for streaming task outputs
        """
        self.stream = stream

    def get_stream(self) -> Queue:
        """
        Get the stream queue.
        
        Returns:
            The stream queue
            
        Raises:
            Exception: If stream hasn't been set
        """
        if self.stream is None:
            raise Exception("Stream is not set. Did you run .stream()?")
        return self.stream

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary.
        
        Returns:
            Dictionary of all key-value pairs
        """
        return {key: state.get_value_with_lock() for key, state in self.states.items()}

    def from_dict(self, data: Dict[str, Any]):
        """
        Load context from dictionary.
        
        Args:
            data: Dictionary of key-value pairs to load
        """
        for key, value in data.items():
            self.set(key, value)
