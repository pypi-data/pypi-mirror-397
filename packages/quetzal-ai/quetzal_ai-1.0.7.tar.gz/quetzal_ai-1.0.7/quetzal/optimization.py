"""
Advanced CPU Optimization Utilities
Quetzal - Powered by Axya-Tech

Maximize CPU performance for ML training
"""

import torch
import torch.nn as nn
import psutil
import os
import multiprocessing as mp
from typing import Optional, Dict, Any
import warnings


class QuantizationOptimizer:
    """
    Model quantization for reduced memory and faster inference
    """
    
    @staticmethod
    def quantize_model_dynamic(model: nn.Module) -> nn.Module:
        """
        Apply dynamic quantization (works on CPU)
        Reduces model size by ~4x and speeds up inference
        """
        print("\n⚡ Applying Dynamic Quantization...")
        
        quantized_model = torch.quantization.quantize_dynamic(
            model,
            {nn.Linear, nn.LSTM, nn.GRU},  # Layers to quantize
            dtype=torch.qint8
        )
        
        # Calculate size reduction
        original_size = sum(p.numel() * p.element_size() for p in model.parameters()) / (1024**2)
        quantized_size = sum(p.numel() * p.element_size() for p in quantized_model.parameters()) / (1024**2)
        
        print(f"✓ Model quantized")
        print(f"   └─ Original size: {original_size:.2f} MB")
        print(f"   └─ Quantized size: {quantized_size:.2f} MB")
        print(f"   └─ Reduction: {(1 - quantized_size/original_size)*100:.1f}%")
        
        return quantized_model
    
    @staticmethod
    def quantize_model_static(
        model: nn.Module, 
        calibration_data: Any
    ) -> nn.Module:
        """
        Apply static quantization (requires calibration data)
        """
        # Placeholder for static quantization
        # Requires calibration step
        return model


class GradientCheckpointing:
    """
    Gradient checkpointing to reduce memory usage during training
    """
    
    @staticmethod
    def enable_gradient_checkpointing(model: nn.Module) -> nn.Module:
        """
        Enable gradient checkpointing to trade compute for memory
        """
        if hasattr(model, 'gradient_checkpointing_enable'):
            model.gradient_checkpointing_enable()
            print("✓ Gradient checkpointing enabled")
        else:
            warnings.warn("Model does not support gradient checkpointing")
        
        return model


class CPUMemoryOptimizer:
    """
    Optimize memory usage on CPU
    """
    
    @staticmethod
    def clear_memory():
        """Clear CPU memory cache"""
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    @staticmethod
    def get_memory_stats() -> Dict[str, float]:
        """Get current memory statistics"""
        mem = psutil.virtual_memory()
        
        return {
            'total_gb': mem.total / (1024**3),
            'available_gb': mem.available / (1024**3),
            'used_gb': mem.used / (1024**3),
            'percent': mem.percent,
        }
    
    @staticmethod
    def monitor_memory(threshold_percent: float = 85.0):
        """
        Monitor memory usage and warn if approaching limit
        """
        stats = CPUMemoryOptimizer.get_memory_stats()
        
        if stats['percent'] > threshold_percent:
            warnings.warn(
                f"⚠️  High memory usage: {stats['percent']:.1f}% "
                f"({stats['used_gb']:.1f}/{stats['total_gb']:.1f} GB)"
            )
            return False
        
        return True


class MixedPrecisionTraining:
    """
    Mixed precision training utilities (where supported on CPU)
    """
    
    @staticmethod
    def enable_mixed_precision() -> bool:
        """
        Enable mixed precision if supported
        Note: Most CPUs don't support fp16, but some newer ones support bfloat16
        """
        
        # Check if CPU supports bfloat16
        if hasattr(torch.cpu, 'is_bf16_supported') and torch.cpu.is_bf16_supported():
            print("✓ BFloat16 supported - enabling mixed precision")
            return True
        else:
            print("ℹ️  Mixed precision not supported on this CPU")
            return False


class DataLoaderOptimizer:
    """
    Optimize data loading for CPU training
    """
    
    @staticmethod
    def get_optimal_num_workers() -> int:
        """
        Calculate optimal number of data loader workers
        """
        # Use 80% of available CPU cores
        num_cores = psutil.cpu_count(logical=False)
        optimal = max(1, int(num_cores * 0.8))
        
        return min(optimal, 8)  # Cap at 8 to avoid overhead
    
    @staticmethod
    def create_optimized_dataloader(
        dataset,
        batch_size: int,
        shuffle: bool = True,
        **kwargs
    ):
        """
        Create a CPU-optimized DataLoader
        """
        from torch.utils.data import DataLoader
        
        num_workers = DataLoaderOptimizer.get_optimal_num_workers()
        
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            pin_memory=False,  # Not useful for CPU
            persistent_workers=True if num_workers > 0 else False,
            **kwargs
        )


class CompilationOptimizer:
    """
    Optimize model using torch.compile (PyTorch 2.0+)
    """
    
    @staticmethod
    def compile_model(model: nn.Module, mode: str = "default") -> nn.Module:
        """
        Compile model for faster execution
        
        Args:
            model: Model to compile
            mode: Compilation mode ('default', 'reduce-overhead', 'max-autotune')
        """
        
        if hasattr(torch, 'compile'):
            try:
                print(f"\n⚡ Compiling model (mode: {mode})...")
                compiled_model = torch.compile(model, mode=mode)
                print("✓ Model compiled successfully")
                return compiled_model
            except Exception as e:
                warnings.warn(f"Could not compile model: {e}")
                return model
        else:
            warnings.warn("torch.compile not available (requires PyTorch 2.0+)")
            return model


class BatchSizeOptimizer:
    """
    Automatically find optimal batch size
    """
    
    @staticmethod
    def find_optimal_batch_size(
        model: nn.Module,
        sample_input: torch.Tensor,
        initial_batch_size: int = 32,
        max_batch_size: int = 256
    ) -> int:
        """
        Find the largest batch size that fits in memory
        """
        
        print("\n🔍 Finding optimal batch size...")
        
        batch_size = initial_batch_size
        optimal = initial_batch_size
        
        model.eval()
        
        while batch_size <= max_batch_size:
            try:
                # Create batch
                batch = sample_input.repeat(batch_size, 1)
                
                # Try forward pass
                with torch.no_grad():
                    _ = model(batch)
                
                optimal = batch_size
                print(f"   ✓ Batch size {batch_size} works")
                
                # Try next size
                batch_size *= 2
                
            except RuntimeError as e:
                if "out of memory" in str(e).lower():
                    print(f"   ✗ Batch size {batch_size} too large")
                    break
                else:
                    raise e
        
        print(f"✓ Optimal batch size: {optimal}")
        return optimal


class ProfilerWrapper:
    """
    Profile model training to identify bottlenecks
    """
    
    @staticmethod
    def profile_training_step(
        model: nn.Module,
        sample_batch: Any,
        num_steps: int = 10
    ):
        """
        Profile a few training steps
        """
        
        print("\n📊 Profiling training steps...")
        
        with torch.profiler.profile(
            activities=[torch.profiler.ProfilerActivity.CPU],
            record_shapes=True,
            profile_memory=True,
        ) as prof:
            
            for _ in range(num_steps):
                output = model(**sample_batch)
                loss = output.loss if hasattr(output, 'loss') else output[0]
                loss.backward()
        
        print("\n" + prof.key_averages().table(sort_by="cpu_time_total", row_limit=10))


# Environment setup
def setup_optimal_cpu_environment():
    """
    Configure environment variables for optimal CPU performance
    """
    
    env_vars = {
        # Intel MKL optimizations
        'MKL_NUM_THREADS': str(psutil.cpu_count(logical=False)),
        'NUMEXPR_NUM_THREADS': str(psutil.cpu_count(logical=False)),
        'OMP_NUM_THREADS': str(psutil.cpu_count(logical=False)),
        
        # OpenMP optimizations
        'KMP_AFFINITY': 'granularity=fine,compact,1,0',
        'KMP_BLOCKTIME': '1',
        
        # TensorFlow (if used)
        'TF_ENABLE_ONEDNN_OPTS': '1',
        
        # PyTorch
        'PYTORCH_ENABLE_MPS_FALLBACK': '1',
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    # PyTorch settings
    # PyTorch settings
    try:
        torch.set_num_threads(psutil.cpu_count(logical=True))
    except RuntimeError:
        pass
        
    try:
        torch.set_num_interop_threads(psutil.cpu_count(logical=False))
    except RuntimeError:
        pass
    
    print("✓ CPU environment optimized")


# Export all classes
__all__ = [
    'QuantizationOptimizer',
    'GradientCheckpointing',
    'CPUMemoryOptimizer',
    'MixedPrecisionTraining',
    'DataLoaderOptimizer',
    'CompilationOptimizer',
    'BatchSizeOptimizer',
    'ProfilerWrapper',
    'setup_optimal_cpu_environment',
]
