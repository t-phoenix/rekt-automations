"""Run number management for flow execution tracking."""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import uuid


class RunManager:
    """Manages run IDs, metadata, and inter-flow data passing."""
    
    def __init__(self, output_dir: str = "./output"):
        """
        Initialize RunManager.
        
        Args:
            output_dir: Base output directory for runs
        """
        self.output_dir = Path(output_dir)
        self.runs_dir = self.output_dir / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_run_id(self) -> str:
        """
        Generate a unique run ID.
        
        Format: run_YYYYMMDD_HHMMSS_XXXX
        
        Returns:
            Unique run ID string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = str(uuid.uuid4())[:4]
        return f"run_{timestamp}_{random_suffix}"
    
    def get_run_dir(self, run_id: str) -> Path:
        """
        Get the directory for a specific run.
        
        Args:
            run_id: Run identifier
            
        Returns:
            Path to run directory
        """
        return self.runs_dir / run_id
    
    def create_run_directory(self, run_id: str) -> Dict[str, Path]:
        """
        Create directory structure for a new run.
        
        Args:
            run_id: Run identifier
            
        Returns:
            Dictionary of subdirectory paths
        """
        run_dir = self.get_run_dir(run_id)
        
        # Create subdirectories
        subdirs = {
            "content": run_dir / "content",
            "memes": run_dir / "memes",
            "video": run_dir / "video",
            "metadata": run_dir / "metadata"
        }
        
        for subdir in subdirs.values():
            subdir.mkdir(parents=True, exist_ok=True)
        
        return subdirs
    
    def save_run_metadata(self, run_id: str, metadata: Dict[str, Any]) -> None:
        """
        Save metadata for a run.
        
        Args:
            run_id: Run identifier
            metadata: Metadata dictionary to save
        """
        run_dir = self.get_run_dir(run_id)
        metadata_file = run_dir / "run_metadata.json"
        
        # Ensure directory exists
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing metadata if it exists
        existing_metadata = {}
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                existing_metadata = json.load(f)
        
        # Merge with new metadata
        existing_metadata.update(metadata)
        
        # Save
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(existing_metadata, f, indent=2, ensure_ascii=False)
    
    def get_run_metadata(self, run_id: str) -> Dict[str, Any]:
        """
        Load metadata for a run.
        
        Args:
            run_id: Run identifier
            
        Returns:
            Metadata dictionary
        """
        metadata_file = self.get_run_dir(run_id) / "run_metadata.json"
        
        if not metadata_file.exists():
            return {}
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_flow_output(
        self,
        run_id: str,
        flow_name: str,
        output_data: Dict[str, Any]
    ) -> None:
        """
        Save output data from a flow.
        
        Args:
            run_id: Run identifier
            flow_name: Name of the flow (text, meme, animation)
            output_data: Output data to save
        """
        run_dir = self.get_run_dir(run_id)
        metadata_dir = run_dir / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = metadata_dir / f"{flow_name}_output.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    def get_flow_output(self, run_id: str, flow_name: str) -> Optional[Dict[str, Any]]:
        """
        Load output data from a flow.
        
        Args:
            run_id: Run identifier
            flow_name: Name of the flow (text, meme, animation)
            
        Returns:
            Output data dictionary or None if not found
        """
        output_file = self.get_run_dir(run_id) / "metadata" / f"{flow_name}_output.json"
        
        if not output_file.exists():
            return None
        
        with open(output_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def run_exists(self, run_id: str) -> bool:
        """
        Check if a run exists.
        
        Args:
            run_id: Run identifier
            
        Returns:
            True if run directory exists
        """
        return self.get_run_dir(run_id).exists()
    
    def list_runs(self) -> list[str]:
        """
        List all run IDs.
        
        Returns:
            List of run ID strings
        """
        if not self.runs_dir.exists():
            return []
        
        return [d.name for d in self.runs_dir.iterdir() if d.is_dir() and d.name.startswith("run_")]
