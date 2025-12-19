"""
AMD ROCm GPU detection for Aegis Vision.

Implements detection strategy for AMD GPUs:
1. PyTorch ROCm API (if available)
2. rocm-smi command (reliable for hardware info)
3. Platform-specific checks
"""

import subprocess
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

logger = logging.getLogger(__name__)


class ROCmGPUDetector:
    """
    AMD ROCm GPU detection using multi-method approach.
    Handles AMD Instinct (MI series) and Radeon cards.
    """
    
    @staticmethod
    def detect_via_rocm_smi() -> Dict[str, Any]:
        """
        Detect AMD GPUs using rocm-smi command.
        
        Returns:
            Dict with detected GPU info:
            {
                "detected": bool,
                "gpus": [...],
                "rocm_version": str | None
            }
        """
        result = {
            "detected": False,
            "gpus": [],
            "rocm_version": None
        }
        
        try:
            # 1. Try to get ROCm version
            try:
                # Often in /opt/rocm/.info/version
                version_path = Path("/opt/rocm/.info/version")
                if version_path.exists():
                    with open(version_path, 'r') as f:
                        result["rocm_version"] = f.read().strip()
            except Exception:
                pass

            # 2. Query GPU information via rocm-smi
            # --showproductname, --showmeminfo are common flags
            cmd = ['rocm-smi', '--showproductname', '--showmeminfo', '--csv']
            
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if proc.returncode != 0:
                # Try simpler version if complex one fails
                cmd = ['rocm-smi', '--showproductname']
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
            if proc.returncode == 0:
                result["detected"] = True
                lines = proc.stdout.strip().split('\n')
                
                # Basic parsing for rocm-smi output
                # Output varies significantly by version, but often looks like:
                # device, product name
                # 0, AMD Instinct MI300X
                
                for line in lines:
                    if "device" in line.lower() or not line.strip():
                        continue
                    
                    try:
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 2:
                            gpu_info = {
                                "index": int(parts[0]) if parts[0].isdigit() else 0,
                                "name": parts[1],
                                "memory": 0,  # Will try to refine
                                "arch": "Unknown"
                            }
                            result["gpus"].append(gpu_info)
                    except Exception:
                        pass
            
            return result
            
        except FileNotFoundError:
            logger.debug("rocm-smi not found in PATH")
            return result
        except subprocess.TimeoutExpired:
            logger.debug("rocm-smi command timed out")
            return result
        except Exception as e:
            logger.debug(f"rocm-smi detection failed: {e}")
            return result

    @staticmethod
    def detect_via_pytorch() -> Dict[str, Any]:
        """
        Detect AMD GPUs via PyTorch ROCm backend.
        
        Returns:
            Dict with PyTorch-specific ROCm info
        """
        result = {
            "available": False,
            "version": None,
            "devices": []
        }
        
        try:
            import torch
            
            # Check for ROCm/HIP version
            rocm_version = getattr(torch.version, 'rocm', None)
            if not rocm_version and hasattr(torch.version, 'hip'):
                rocm_version = torch.version.hip
                
            if rocm_version:
                result["version"] = rocm_version
                
            if torch.cuda.is_available():
                # On ROCm, torch.cuda.is_available() is True if ROCm is working
                result["available"] = True
                
                for i in range(torch.cuda.device_count()):
                    name = torch.cuda.get_device_name(i)
                    props = torch.cuda.get_device_properties(i)
                    
                    device_info = {
                        "index": i,
                        "name": name,
                        "memory": round(props.total_memory / (1024**3), 2),
                    }
                    
                    # ROCm specific properties if available
                    if hasattr(props, 'gcnArchName'):
                        device_info["arch"] = props.gcnArchName
                        
                    result["devices"].append(device_info)
                    
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"PyTorch ROCm detection failed: {e}")
            
        return result

    @staticmethod
    def detect() -> Dict[str, Any]:
        """
        Main detection entry point.
        """
        smi_info = ROCmGPUDetector.detect_via_rocm_smi()
        torch_info = ROCmGPUDetector.detect_via_pytorch()
        
        detected = smi_info["detected"] or torch_info["available"]
        
        return {
            "detected": detected,
            "method": "rocm-smi" if smi_info["detected"] else "PyTorch ROCm",
            "rocm_version": torch_info["version"] or smi_info["rocm_version"],
            "gpus": torch_info["devices"] if torch_info["devices"] else smi_info["gpus"],
            "pytorch_available": torch_info["available"]
        }
