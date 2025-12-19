"""
Quetzal - Fast CPU Training for Low-Resource Languages
Powered by Axya-Tech
"""

import torch
import torch.nn as nn
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import warnings
import psutil
import os
from typing import Optional, Tuple, Dict, Any
import time
import sys

warnings.filterwarnings('ignore')

QUETZAL_LOGO = """
\033[92m\033[1m
╔═════════════════════════════════════════════════════════════════════════════╗
║                                                                             ║
║   ██████╗  ██╗   ██╗ ███████╗ ████████╗ ███████╗  █████╗  ██╗               ║
║  ██╔═══██╗ ██║   ██║ ██╔════╝ ╚══██╔══╝ ╚══███╔╝ ██╔══██╗ ██║               ║
║  ██║   ██║ ██║   ██║ █████╗      ██║      ███╔╝  ███████║ ██║               ║
║  ██║▄▄ ██║ ██║   ██║ ██╔══╝      ██║     ███╔╝   ██╔══██║ ██║               ║
║  ╚██████╔╝ ╚██████╔╝ ███████╗    ██║    ███████╗ ██║  ██║ ███████╗          ║
║   ╚══▀▀═╝   ╚═════╝  ╚══════╝    ╚═╝    ╚══════╝ ╚═╝  ╚═╝ ╚══════╝          ║
║                                                                             ║
║  ─────────────────────────────────────────────────────────────────────      ║
║                                                                             ║
║  Lightning-Fast CPU Training for Low-Resource Language Models               ║
║  Optimized Performance • Enterprise-Ready • Production-Grade                ║
║  Powered by Axya-Tech                                                       ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
\033[0m
"""

# Print logo on import if in interactive mode or main script
if hasattr(sys, 'ps1') or __name__ == '__main__' or 'ipykernel' in sys.modules:
    try:
        print(QUETZAL_LOGO)
    except Exception:
        pass

class CPUOptimizer:
    """Advanced CPU optimization techniques"""
    
    @staticmethod
    def optimize_cpu_performance():
        """Enable CPU optimizations for faster training"""
        # Enable oneDNN optimizations
        os.environ['TF_ENABLE_ONEDNN_OPTS'] = '1'
        os.environ['KMP_AFFINITY'] = 'granularity=fine,compact,1,0'
        os.environ['KMP_BLOCKTIME'] = '1'
        
        # Optimize PyTorch for CPU
        try:
            torch.set_num_threads(psutil.cpu_count(logical=True))
        except RuntimeError:
            pass

        try:
            torch.set_num_interop_threads(psutil.cpu_count(logical=False))
        except RuntimeError:
            pass
        
        if hasattr(torch, 'set_float32_matmul_precision'):
            torch.set_float32_matmul_precision('high')
        
        print(f"🦅 Quetzal CPU Optimization Enabled")
        print(f"   └─ Using {torch.get_num_threads()} threads")
        print(f"   └─ Available RAM: {psutil.virtual_memory().available / (1024**3):.1f} GB")
    
    @staticmethod
    def get_optimal_batch_size() -> int:
        """Calculate optimal batch size based on available RAM"""
        available_ram_gb = psutil.virtual_memory().available / (1024**3)
        
        if available_ram_gb > 16:
            return 8
        elif available_ram_gb > 8:
            return 4
        else:
            return 2

class GPUOptimizer:
    """Advanced GPU optimization techniques"""
    
    @staticmethod
    def optimize_gpu_performance():
        """Enable GPU optimizations for faster training"""
        if not torch.cuda.is_available():
            print("⚠️ GPU not available, skipping GPU optimization")
            return
            
        # Enable TF32 for Ampere and newer GPUs
        if hasattr(torch.backends.cuda, 'matmul'):
            torch.backends.cuda.matmul.allow_tf32 = True
        
        if hasattr(torch.backends.cudnn, 'allow_tf32'):
            torch.backends.cudnn.allow_tf32 = True
            
        # Enable CuDNN benchmark for consistent input sizes
        torch.backends.cudnn.benchmark = True
        
        print(f"🦅 Quetzal GPU Optimization Enabled")
        print(f"   └─ Device: {torch.cuda.get_device_name(0)}")
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"   └─ VRAM: {vram_gb:.2f} GB")


class FastLanguageModel:
    """
    Quetzal's Fast Language Model optimized for CPU training
    with minimal data requirements and maximum accuracy
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.cpu_optimized = False
    
    @staticmethod
    def from_pretrained(
        model_name: str,
        max_seq_length: int = 2048,
        dtype: Optional[torch.dtype] = None,
        load_in_4bit: bool = True,
        device_map: str = "auto",
        device: str = "auto",
        **kwargs
    ) -> Tuple[Any, Any]:
        """
        Load a pretrained model with Quetzal optimizations
        
        Args:
            model_name: HuggingFace model name or path
            max_seq_length: Maximum sequence length
            dtype: Data type (None for auto)
            load_in_4bit: Use 4-bit quantization for memory efficiency
            device_map: Device mapping strategy
            device: 'cpu', 'cuda', or 'auto' (default)
        
        Returns:
            (model, tokenizer) tuple
        """
        
        # Determine device
        device = device.lower()
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if device == "cuda" and not torch.cuda.is_available():
            print("\n⚠️  CUDA requested but not available. Falling back to CPU.")
            device = "cpu"

        # Optimization Logic
        if device == "cpu":
            # CPU Optimization: Disable 4-bit on CPU to favor speed
            if load_in_4bit:
                print("\n⚠️  Notice: Disabling 4-bit quantization for CPU training speed.")
                load_in_4bit = False
        
        print("\n🦅 Quetzal 2025.12.17: Fast Training Initialized")
        print(f"   Model: {model_name}")
        print(f"   Platform: {device.upper()}-Optimized")
        print(f"   Quantization: {'4-bit' if load_in_4bit else 'None (Float32)'}")
        
        # Apply Hardware Optimizations
        if device == "cpu":
            CPUOptimizer.optimize_cpu_performance()
        else:
            GPUOptimizer.optimize_gpu_performance()
        
        # Load tokenizer
        print("\n📥 Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            use_fast=True,
        )
        
        # Ensure tokenizer has pad token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.pad_token_id = tokenizer.eos_token_id
        
        # Configure model loading
        model_kwargs = {
            "trust_remote_code": True,
            "low_cpu_mem_usage": True,
            "torch_dtype": dtype if dtype else (torch.float16 if device == "cuda" else torch.float32),
        }
        
        # Pass load_in_4bit if enabled
        if load_in_4bit:
            model_kwargs["load_in_4bit"] = True
        
        print("📥 Loading model...")
        start_time = time.time()
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map=device_map,
            **model_kwargs,
            **kwargs
        )
        
        # Move to CPU explicitly if not using device_map and on CPU
        # For GPU, 'device_map="auto"' usually handles it, or typical Trainer flow
        if device == "cpu" and "device_map" not in kwargs and not load_in_4bit:
            model = model.to('cpu')
        
        load_time = time.time() - start_time
        print(f"✓ Model loaded in {load_time:.2f}s")
        
        # Model size info
        param_count = sum(p.numel() for p in model.parameters())
        print(f"   └─ Parameters: {param_count / 1e6:.1f}M")
        
        return model, tokenizer
    
    @staticmethod
    def get_peft_model(
        model: Any,
        r: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.05,
        target_modules: Optional[list] = None,
        task_type: str = "CAUSAL_LM",
        **kwargs
    ) -> Any:
        """
        Apply LoRA (Low-Rank Adaptation) for efficient fine-tuning
        
        Args:
            model: Base model
            r: LoRA rank (lower = fewer parameters)
            lora_alpha: LoRA alpha parameter
            lora_dropout: Dropout rate
            target_modules: Modules to apply LoRA to
            task_type: Type of task
        
        Returns:
            LoRA-enabled model
        """
        
        print("\n🔧 Applying Quetzal LoRA Configuration...")
        
        if target_modules is None:
            # Default target modules for common architectures
            target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", 
                            "gate_proj", "up_proj", "down_proj"]
        
        lora_config = LoraConfig(
            r=r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            target_modules=target_modules,
            bias="none",
            task_type=task_type,
            **kwargs
        )
        
        model = get_peft_model(model, lora_config)
        
        # Calculate trainable parameters
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())
        trainable_percent = 100 * trainable_params / total_params
        
        print(f"✓ LoRA Applied")
        print(f"   └─ Trainable params: {trainable_params:,} ({trainable_percent:.2f}%)")
        print(f"   └─ LoRA rank: {r}")
        
        return model


class DhivehiDataAugmenter:
    """
    Advanced data augmentation for low-resource languages like Dhivehi
    to maximize accuracy with minimal data
    """
    
    @staticmethod
    def back_translation(text: str, tokenizer, model) -> list:
        """Simulate back-translation augmentation"""
        # Placeholder for back-translation logic
        return [text]
    
    @staticmethod
    def paraphrase_generation(text: str) -> list:
        """Generate paraphrases of the input text"""
        # Simple rule-based paraphrasing
        variations = [text]
        
        # Add variations with different punctuation
        if text.endswith('.'):
            variations.append(text[:-1] + '!')
        
        return variations
    
    @staticmethod
    def augment_dataset(dataset, tokenizer, model=None, augmentation_factor: int = 3):
        """
        Augment dataset to increase training data
        
        Args:
            dataset: Input dataset
            tokenizer: Tokenizer
            model: Model for advanced augmentation
            augmentation_factor: How many times to augment each sample
        
        Returns:
            Augmented dataset
        """
        print(f"\n📊 Augmenting dataset (factor: {augmentation_factor}x)...")
        
        augmented_data = []
        original_size = len(dataset)
        
        for item in dataset:
            text = item['text'] if 'text' in item else str(item)
            augmented_data.append({'text': text})
            
            # Add augmented versions
            for _ in range(augmentation_factor - 1):
                variations = DhivehiDataAugmenter.paraphrase_generation(text)
                for var in variations[:1]:  # Take first variation
                    augmented_data.append({'text': var})
        
        print(f"✓ Dataset augmented: {original_size} → {len(augmented_data)} samples")
        
        return augmented_data


class QuetzalTrainer:
    """
    Optimized trainer for CPU with aggressive memory management
    """
    
    @staticmethod
    def create_training_args(
        output_dir: str = "./quetzal-output",
        num_train_epochs: int = 3,
        per_device_train_batch_size: Optional[int] = None,
        learning_rate: float = 2e-4,
        warmup_steps: int = 100,
        logging_steps: int = 10,
        save_steps: int = 500,
        **kwargs
    ) -> TrainingArguments:
        """
        Create optimized training arguments for CPU
        """
        
        if per_device_train_batch_size is None:
            per_device_train_batch_size = CPUOptimizer.get_optimal_batch_size()
        
        return TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=per_device_train_batch_size,
            gradient_accumulation_steps=4,  # Simulate larger batches
            learning_rate=learning_rate,
            warmup_steps=warmup_steps,
            logging_steps=logging_steps,
            save_steps=save_steps,
            save_total_limit=3,
            fp16=False,  # CPU doesn't support fp16
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            no_cuda=True,  # Force CPU
            dataloader_num_workers=2,
            remove_unused_columns=False,
            **kwargs
        )


# Export main classes
__all__ = [
    'FastLanguageModel',
    'DhivehiDataAugmenter', 
    'QuetzalTrainer',
    'CPUOptimizer'
]

__version__ = "1.0.0"
__author__ = "Axya-Tech"
