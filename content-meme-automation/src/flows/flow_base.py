"""Base class for all flows."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

from ..utils.run_manager import RunManager
from ..config.flow_config import FlowConfig


class FlowBase(ABC):
    """Base class for all automation flows."""
    
    def __init__(
        self,
        run_id: Optional[str] = None,
        config: Optional[FlowConfig] = None,
        override_string: Optional[str] = None
    ):
        """
        Initialize flow.
        
        Args:
            run_id: Existing run ID to continue, or None to create new
            config: FlowConfig instance or None to create from defaults
            override_string: Configuration override string
        """
        # Initialize config
        if config is None:
            config = FlowConfig(override_string=override_string)
        elif override_string:
            # Apply overrides to existing config
            config._apply_overrides(override_string)
        
        self.config = config
        
        # Initialize run manager
        output_path = self.config.get("output_path", "./output")
        self.run_manager = RunManager(output_path)
        
        # Set or generate run ID
        if run_id:
            if not self.run_manager.run_exists(run_id):
                raise ValueError(f"Run ID does not exist: {run_id}")
            self.run_id = run_id
        else:
            self.run_id = self.run_manager.generate_run_id()
        
        # Create run directory structure
        self.run_dirs = self.run_manager.create_run_directory(self.run_id)
        
        # Store flow name (to be set by subclass)
        self.flow_name = self.__class__.__name__.replace("Flow", "").lower()
    
    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """
        Execute the flow.
        
        Returns:
            Flow output dictionary
        """
        pass
    
    def save_output(self, output_data: Dict[str, Any]) -> None:
        """
        Save flow output.
        
        Args:
            output_data: Output data to save
        """
        self.run_manager.save_flow_output(self.run_id, self.flow_name, output_data)
    
    def load_previous_flow_output(self, flow_name: str) -> Optional[Dict[str, Any]]:
        """
        Load output from a previous flow in the same run.
        
        Args:
            flow_name: Name of the previous flow (text, meme, animation)
            
        Returns:
            Previous flow output or None if not found
        """
        return self.run_manager.get_flow_output(self.run_id, flow_name)
    
    def update_run_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Update run metadata.
        
        Args:
            metadata: Metadata to add/update
        """
        self.run_manager.save_run_metadata(self.run_id, metadata)
    
    def validate_config(self) -> None:
        """
        Validate configuration and raise error if invalid.
        
        Raises:
            ValueError: If configuration is invalid
        """
        is_valid, errors = self.config.validate()
        if not is_valid:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_msg)
    
    def print_banner(self, title: str) -> None:
        """
        Print a flow banner.
        
        Args:
            title: Banner title
        """
        print("\n" + "=" * 60)
        print(f"🚀 {title}")
        print("=" * 60)
        print(f"Run ID: {self.run_id}")
        print(f"Flow: {self.flow_name}")
        print("=" * 60 + "\n")
