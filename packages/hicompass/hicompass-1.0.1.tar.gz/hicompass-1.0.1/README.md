# Hi-Compass

Hi-Compass (High-resolution Chromatin Organization Mapping from ATAC-Seq Signals) is a depth-aware multi-modal deep learning framework for predicting cell-type-specific chromatin interactions from ATAC-seq data.

## Installation

**Important**: Hi-Compass requires PyTorch but does not install it automatically, as the correct version depends on your system and CUDA configuration.

1. First, install PyTorch following the instructions at [pytorch.org](https://pytorch.org/get-started/locally/)

2. Then install Hi-Compass:
```bash
pip install hicompass
```

3. If you plan to train models (optional):
```bash
pip install hicompass[train]
```

## Documentation

Full documentation and tutorials are available at: https://github.com/EndeavourSyc/Hi-Compass

## License

MIT License
