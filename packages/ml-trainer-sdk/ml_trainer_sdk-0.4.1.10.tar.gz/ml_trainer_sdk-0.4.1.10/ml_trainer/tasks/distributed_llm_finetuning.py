import os
import yaml
import math
from pathlib import Path
from datasets import Dataset, DatasetDict
from sklearn.model_selection import train_test_split
import pandas as pd
from typing import Dict, List, Callable, Optional, Union

# Local application
from ml_trainer.base import BaseDataset, AbstractModelArchitecture
from ml_trainer.trainer import BaseTrainer
from ml_trainer.tasks.task_factory import AbstractTaskFactory
from ml_trainer.utils.metrics import LLMFinetuneMetrics
from ml_trainer.utils.logger import BaseLogger


class DistributedLLMFineTuningDataset(BaseDataset):
    """
    Flexible dataset loader / formatter for distributed training with Axolotl.

    Expected dataset config (example):
    dataset_config = {
        "source": "/path/to/file.json",   # or DataFrame, or dict with 'train'/'test'
        "format_fn": optional_callable,   # function(row) -> List[{"role","content"}]
        "test_size": 0.1,
        "random_state": 42,
    }

    Behavior:
    - If `format_fn` provided, use it to convert each row -> messages.
    - Else, accept rows that already have 'messages'.
    """

    def __init__(
        self,
        tokenizer=None,
        system_prompt: str = None,
        config: Optional[dict] = None,
        **kwargs,
    ):
        self.tokenizer = tokenizer
        self.system_prompt = system_prompt or "You are a helpful assistant."
        self.config = config or {}
        super().__init__(config=self.config, **kwargs)

        # Extract config values
        if "source" not in self.config:
            raise ValueError("config must contain 'source' key")

        self.data_source = self.config["source"]
        self.test_size = self.config.get("test_size", None)
        self.format_fn = self.config.get("format_fn", None)

        # If user passes "default" or None, we will infer automatically later
        if isinstance(self.format_fn, str):
            if self.format_fn.lower() == "default":
                self.format_fn = self._default_format_fn
                print("Applying the default format function")
            else:
                raise ValueError(f"Unknown format function name: {self.format_fn}")

    def _load_raw_data(self) -> pd.DataFrame:
        """Load data from various sources"""
        # Pandas DataFrame -> return as-is (handled downstream)
        if isinstance(self.data_source, pd.DataFrame):
            return self.data_source

        # HuggingFace DatasetDict -> normalize to dict of record-lists
        if isinstance(self.data_source, DatasetDict):
            normalized = {}
            for split, ds in self.data_source.items():
                normalized[split] = [dict(r) for r in ds]
            return normalized

        # Single HuggingFace Dataset -> treat as 'train' split
        if isinstance(self.data_source, Dataset):
            return {"train": [dict(r) for r in self.data_source]}

        # If user passed a plain list of records (already formatted), treat as train
        if isinstance(self.data_source, list):
            return {"train": self.data_source}

        # If a dict was passed, normalize any Dataset/DataFrame values inside
        if isinstance(self.data_source, dict):
            normalized = {}
            for k, v in self.data_source.items():
                if isinstance(v, Dataset):
                    normalized[k] = [dict(r) for r in v]
                elif isinstance(v, pd.DataFrame):
                    normalized[k] = v.to_dict("records")
                elif isinstance(v, list):
                    normalized[k] = v
                else:
                    normalized[k] = v
            return normalized
        elif isinstance(self.data_source, (str, Path)):
            path = Path(self.data_source)
            if path.suffix == ".json":
                return pd.read_json(path)
            elif path.suffix == ".jsonl":
                return pd.read_json(path, lines=True)
            elif path.suffix == ".csv":
                return pd.read_csv(path)
            elif path.suffix == ".parquet":
                return pd.read_parquet(path)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
        else:
            raise ValueError(f"Unsupported data_source type: {type(self.data_source)}")

    def _default_format_fn(self, row: dict):
        """Default format function for (instruction, response) datasets"""
        if "instruction" in row and "response" in row:
            return [
                {"role": "user", "content": row["instruction"]},
                {"role": "assistant", "content": row["response"]},
            ]
        else:
            raise ValueError(
                "Default format function expects columns 'instruction' and 'response'. "
                f"Got keys: {list(row.keys())}"
            )

    def load_dataset(self) -> Dict[str, Dataset]:
        """Load and format dataset for Axolotl"""
        raw_data = self._load_raw_data()

        # Handle pre-split data
        if isinstance(raw_data, dict) and "train" in raw_data:
            train_data = raw_data["train"]
            test_data = raw_data.get("test", [])
        else:
            # Split the data
            if isinstance(raw_data, pd.DataFrame):
                if self.test_size is None:
                    train_data = raw_data.to_dict("records")
                    test_data = []
                else:
                    train_df, test_df = train_test_split(
                        raw_data,
                        test_size=self.test_size,
                        random_state=self.config.get("random_state", 42),
                    )
                    train_data = train_df.to_dict("records")
                    test_data = test_df.to_dict("records")
            else:
                raise ValueError("Data must be DataFrame or dict with train/test keys")

        # For Axolotl, we need to ensure data has messages format
        formatted_train = []
        for item in train_data:
            if self.format_fn:
                messages = self.format_fn(item)
            else:
                if "messages" not in item:
                    raise ValueError(
                        "Data must have 'messages' key with standard format, "
                        "or you must provide a 'format_fn' to convert your data. "
                        f"Got keys: {list(item.keys())}"
                    )
                messages = item["messages"]
            
            formatted_train.append({"messages": messages})

        formatted_test = []
        for item in test_data:
            if self.format_fn:
                messages = self.format_fn(item)
            else:
                if "messages" not in item:
                    raise ValueError(
                        "Data must have 'messages' key with standard format, "
                        "or you must provide a 'format_fn' to convert your data. "
                        f"Got keys: {list(item.keys())}"
                    )
                messages = item["messages"]
            
            formatted_test.append({"messages": messages})

        self.formatted_dataset = {
            "train": Dataset.from_list(formatted_train),
            "test": Dataset.from_list(formatted_test) if formatted_test else None,
        }
        return self.formatted_dataset


class DistributedLLMModel(AbstractModelArchitecture):
    """Model wrapper for Axolotl-based distributed training"""
    
    def __init__(self, model_name, config=None):
        self.config = config or {}
        self.model_name = model_name or self.config.get("model_name")
        self._model_loaded = False
        
        # Axolotl configuration
        self.axolotl_config = {}
        self.model = None
        self.tokenizer = None

    def _load_model_if_needed(self):
        """Lazy loading - model will be loaded by Axolotl during training"""
        if not self._model_loaded:
            print(f"Model {self.model_name} will be loaded by Axolotl during training...")
            self._model_loaded = True

    def get_tokenizer(self):
        """Get tokenizer - for Axolotl, we might not need to pre-load"""
        if self.tokenizer is None:
            from transformers import AutoTokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        return self.tokenizer

    def get_model(self):
        """Model will be loaded by Axolotl"""
        self._load_model_if_needed()
        return self.model

    def forward(self, x):
        """Forward pass - handled by Axolotl"""
        if self.model is None:
            raise ValueError("Model not loaded - should be loaded by Axolotl trainer")
        return self.model(x)

    def save(self, path):
        """Save model - handled by Axolotl"""
        print(f"Model saving is handled by Axolotl at: {path}")

    def load(self, path):
        """Load model - handled by Axolotl"""
        print(f"Model loading from: {path}")


class DistributedLLMTrainer(BaseTrainer):
    """Trainer using Axolotl for distributed LLM finetuning"""
    
    def __init__(self, model, tokenizer, dataset, config, metrics=None, model_wrapper=None):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config
        self.model_wrapper = model_wrapper
        self.metrics = metrics or {}
        self.dataset = dataset

        self.save_model_flag = config.get("save_model", False)
        self.output_dir = config.get("output_dir", "/tmp/output")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.log_callbacks = config.get("log_callbacks", [])
        for cb in self.log_callbacks:
            cb.set_trainer(self)

        # Get dataset splits
        train_dataset = dataset["train"]
        val_dataset = dataset.get("test")

        # Save dataset to disk for Axolotl to use
        self.dataset_path = Path(self.output_dir) / "dataset"
        self.dataset_path.mkdir(parents=True, exist_ok=True)
        
        train_path = self.dataset_path / "train"
        train_path.mkdir(parents=True, exist_ok=True)
        
        # Save as JSONL for Axolotl
        import json
        train_file = train_path / "data.jsonl"
        print(f"Saving {len(train_dataset)} training samples to: {train_file}")
        with open(train_file, "w") as f:
            for item in train_dataset:
                f.write(json.dumps(item) + "\n")
        
        print(f"Saved training dataset to: {train_file}")

        # Create Axolotl configuration
        self.axolotl_config = self._create_axolotl_config(str(train_path))
        
        # Save config to file
        config_path = Path(self.output_dir) / "axolotl_config.yml"
        with open(config_path, "w") as f:
            yaml.dump(self.axolotl_config, f, default_flow_style=False)
        
        print(f"Axolotl config saved to: {config_path}")
        self.config_path = config_path

    def _create_axolotl_config(self, dataset_path: str) -> dict:
        """Create Axolotl configuration dictionary"""
        return {
            "base_model": self.model_wrapper.model_name,
            "model_type": "AutoModelForCausalLM",
            "tokenizer_type": "AutoTokenizer",

            # ===== DISTRIBUTION OFF =====
            "distributed_type": self.config.get("distributed_type", "off"),
            "num_processes": self.config.get("num_processes", 1),
            "ddp": self.config.get("ddp", False),
            "fsdp": self.config.get("fsdp", []),
            "fsdp_config": self.config.get("fsdp_config", {}),
            "deepspeed": self.config.get("deepspeed", None),
            "ddp_find_unused_parameters": self.config.get("ddp_find_unused_parameters", False),
            "local_rank": self.config.get("local_rank", None),
            "world_size": self.config.get("world_size", None),
            "ddp_timeout": self.config.get("ddp_timeout", 1800),

            
            # Dataset configuration
            "datasets": [
                {
                    "path": dataset_path,
                    "type": self.config.get("dataset_type", "chat_template"),
                    "field_messages": self.config.get("field_messages", "messages"),
                    "message_field_role": self.config.get("message_field_role", "role"),
                    "message_field_content": self.config.get("message_field_content", "content"),
                    "chat_template": self.config.get("chat_template", "chatml"),
                }
            ],
            
            # Training hyperparameters
            "sequence_len": self.config.get("max_seq_length", 2048),
            "sample_packing": self.config.get("sample_packing", False),
            "pad_to_sequence_len": self.config.get("pad_to_sequence_len", True),
            
            # LoRA configuration
            "adapter": self.config.get("adapter", "lora"),
            "lora_r": self.config.get("lora_r", 16),
            "lora_alpha": self.config.get("lora_alpha", 32),
            "lora_dropout": self.config.get("lora_dropout", 0.05),
            "lora_target_modules": self.config.get(
                "lora_target_modules", 
                ["q_proj", "k_proj", "v_proj", "o_proj"]
            ),
            
            # Training arguments
            "output_dir": self.output_dir,
            "num_epochs": self.config.get("epochs", 1),
            "micro_batch_size": self.config.get("batch_size", 1),
            "gradient_accumulation_steps": self.config.get("gradient_accumulation_steps", 4),
            "learning_rate": self.config.get("learning_rate", 2e-5),
            "warmup_steps": self.config.get("warmup_steps", 10),
            "logging_steps": self.config.get("logging_steps", 1),
            "save_steps": self.config.get("save_steps", 50),
            "eval_steps": self.config.get("eval_steps", 50),
            "save_total_limit": self.config.get("save_total_limit", 3),
            
            # Optimization
            "gradient_checkpointing": self.config.get("gradient_checkpointing", True),
            "bf16": self.config.get("bf16", True),
            "tf32": self.config.get("tf32", True),
            "flash_attention": self.config.get("flash_attention", False),
            
            # Other settings
            "load_in_8bit": self.config.get("load_in_8bit", False),
            "load_in_4bit": self.config.get("load_in_4bit", False),
            "strict": False,
        }

    def training_step(self, batch):
        """Training step - handled by Axolotl"""
        pass

    def validation_step(self, batch):
        """Validation step - handled by Axolotl"""
        pass

    def run(self):
        """Run Axolotl training using CLI"""
        import subprocess
        import sys
        
        try:
            # Log training start
            if "train" in self.metrics:
                self.metrics["train"].on_train_begin()
            
            print(f"Starting Axolotl training with config: {self.config_path}")
            
            # Run Axolotl via CLI
            cmd = [
                sys.executable, "-m", "axolotl.cli.train",
                str(self.config_path)
            ]
            
            # Run the command and stream output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output in real-time
            for line in process.stdout:
                print(line, end='')
            
            # Wait for completion
            return_code = process.wait()
            
            if return_code != 0:
                raise RuntimeError(f"Axolotl training failed with exit code {return_code}")
            
            print("Training completed successfully!")
            
            # Log training end
            if "train" in self.metrics:
                self.final_metrics = self.metrics["train"].on_train_end()
                for callback in self.log_callbacks:
                    callback.on_train_end()
            
            return {"status": "success", "output_dir": self.output_dir}
            
        except Exception as e:
            print(f"Error during Axolotl training: {e}")
            import traceback
            traceback.print_exc()
            raise

    def evaluate(self):
        """Run evaluation - handled by Axolotl during training"""
        print("Evaluation is handled by Axolotl during training")
        return {}


class DistributedLLMTaskFactory(AbstractTaskFactory):
    """Factory for creating distributed LLM finetuning components using Axolotl"""
    
    def __init__(self):
        self._model_instance = None

    def create_dataset(self, config):
        """Create dataset for distributed training"""
        # Get dataset configuration
        dataset_config = config.get("dataset_config") or {}

        if "source" not in dataset_config:
            raise ValueError("dataset_config must contain a 'source' key")

        print(f"Creating DistributedLLMFineTuningDataset with config: {dataset_config}")

        # For Axolotl, we might not need tokenizer at this stage
        return DistributedLLMFineTuningDataset(
            tokenizer=None,
            system_prompt=config.get("system_prompt"),
            config=dataset_config,
        )

    def create_model(self, config):
        """Create model wrapper for Axolotl training"""
        if self._model_instance is None:
            model_config = config.get("model_config", {})
            print(f"Creating DistributedLLMModel with config: {model_config}")

            model_name = config.get("model_name") or model_config.get("model_name")
            if model_name is None:
                raise ValueError(
                    "Model name must be specified in config or model_config"
                )

            self._model_instance = DistributedLLMModel(
                model_name=model_name,
                config=model_config,
            )
        return self._model_instance
    
    def create_metrics(self, config):
        """Create metrics trackers"""
        train_metrics = LLMFinetuneMetrics()
        val_metrics = LLMFinetuneMetrics()
        return {"train": train_metrics, "val": val_metrics}

    def create_trainer(self, model, dataset, metrics, config):
        """Create Axolotl-based trainer"""
        dataset = dataset.load_dataset()

        trainer_config = config.get("trainer_config", {})
        print(f"Creating DistributedLLMTrainer with config: {trainer_config}")

        return DistributedLLMTrainer(
            model=None,  # Model loaded by Axolotl
            tokenizer=model.get_tokenizer(),
            dataset=dataset,
            model_wrapper=model,
            config=trainer_config,
            metrics=metrics,
        )
