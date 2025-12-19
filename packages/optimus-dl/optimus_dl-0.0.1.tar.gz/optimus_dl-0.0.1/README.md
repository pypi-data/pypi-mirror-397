# LLM Baselines

A clean, modular framework for training large language models with modern PyTorch features and best practices.

## Features

- **Functional Architecture**: Clean separation of concerns with functional decomposition
- **Universal Metrics System**: Lazy evaluation metrics with distributed aggregation
- **Flexible Configuration**: Hydra-based configuration system with modular components
- **Modern PyTorch**: Mixed precision training, distributed checkpointing, gradient accumulation
- **Extensible Design**: Plugin-based architecture for models, optimizers, datasets, and metrics

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd llm-baselines2

# Install dependencies
pip install -e .
```

### Training

```bash
# Train with default configuration (Llama2 on sample data)
python scripts/train.py

# Train with custom configuration
python scripts/train.py model=llama2 data=custom_dataset
```

## Architecture

### Core Components

- **`optimus_dl/core/`** - Core training utilities (device setup, training loops, checkpointing)
- **`optimus_dl/modules/`** - Modular components (models, optimizers, criteria, data)
- **`optimus_dl/recipe/`** - Training recipes that orchestrate components
- **`configs/`** - Hydra configuration files
- **`scripts/`** - Training and evaluation scripts

### Key Features

#### Universal Metrics System
```python
# Lazy evaluation - expensive operations only when needed
log_averaged("loss", lambda: loss.item(), weight=1.0)

# Automatic distributed aggregation
metrics = compute_metrics("train", aggregate=True, collective=collective)
```

#### Functional Training Components
```python
# Device setup with structured returns
device_setup = setup_device_and_collective(use_gpu=True)

# Clean training iteration
run_training_iteration(cfg, model, optimizer, criterion, data_iter, context)
```

#### Flexible Configuration
```yaml
# configs/model/llama2.yaml
_target_: optimus_dl.modules.model.llama2.Llama2Model
vocab_size: 32000
dim: 4096
n_layers: 32
```

## Supported Models

- **Llama2**: Llama 2 architecture implementation
- **GPT-2**: GPT-2 architecture implementation

## Supported Datasets

- **HuggingFace Datasets**: Integration with HF datasets library
- **Tokenized Flat Dataset**: Efficient pre-tokenized dataset format
- **Custom Datasets**: Easy to extend with your own data loaders

## Configuration

The framework uses Hydra for configuration management. Key configuration files:

- `configs/train_llama.yaml` - Main training configuration
- `configs/model/` - Model configurations
- `configs/data/` - Dataset configurations
- `configs/lr_scheduler/` - Learning rate scheduler configurations

### Example Training Configuration

```yaml
defaults:
  - model: llama2
  - data: llama3
  - lr_scheduler: llama3
  - criterion: cross_entropy

common:
  use_gpu: true
  log_freq: 10
  save_freq: 100
  eval_freq: 100

optimization:
  iterations: 1000
  acc_steps: 4
  clip_grad_norm: 1.0
  amp:
    enabled: true
    dtype: torch.bfloat16
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/data/
```

### Code Formatting

```bash
# Format code
black .
isort .
```

### Adding New Components

1. **Models**: Extend `BaseModel` in `optimus_dl/modules/model/`
2. **Datasets**: Implement dataset loaders in `optimus_dl/modules/data/datasets/`
3. **Optimizers**: Add optimizers in `optimus_dl/modules/optim/`
4. **Metrics**: Create custom metrics in `optimus_dl/modules/metrics/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run formatting and tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with PyTorch and Hydra
- Inspired by modern LLM training best practices
- Designed for research and production use
