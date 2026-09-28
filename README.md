# 🪓 GPT-Axe

A GPT trained from scratch on the collected works of Brazilian author Machado de Assis ('Axe of Assis' in a literal translation).

GPT-Axe is an educational language-modeling project. It includes a reproducible corpus builder, a PyTorch implementation of a decoder-only Transformer, a complete training loop, and examples of Portuguese text generation from Machado-inspired prompts.

## What is included

- A corpus of 116 works across novels, short stories, poetry, chronicles, theatre, criticism, translations, and miscellaneous writing
- A character-level tokenizer with a fixed Portuguese-language vocabulary
- A 19.2M-parameter causal Transformer implemented directly in PyTorch
- Training and validation loops with learning-rate warmup, cosine decay, gradient clipping, and AdamW
- Autoregressive generation with temperature and top-k sampling
- Automatic device selection for CUDA, Apple Silicon (MPS), or CPU

## Model architecture

| Setting | Value |
| --- | ---: |
| Parameters | 19,238,400 |
| Context length | 512 characters |
| Embedding size | 512 |
| Attention heads | 8 |
| Transformer blocks | 6 |
| Dropout | 0.1 |
| Batch size | 32 |
| Training steps | 12,500 |

The model uses learned token and positional embeddings, pre-layer-normalized Transformer blocks, causal multi-head self-attention, GELU feed-forward layers, and tied input/output embedding weights.

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/lucasdbr05/gpt-axe.git
cd gpt-axe
```

### 2. Create an environment and install dependencies

Python 3.10+ and PyTorch 2.0+ are recommended.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt jupyterlab
```

### 3. Open the notebook

```bash
jupyter lab train.ipynb
```

Run the notebook from top to bottom to prepare the data, create the model, train it, save a checkpoint, and generate samples. The default configuration is intended for GPU training; running all 12,500 steps on a CPU can take a long time. Reduce `batch_size`, `block_size`, `n_embd`, `n_layer`, or `max_iters` if memory or training time is limited.

## Dataset

The consolidated UTF-8 corpus is already available at `data/machado_de_assis_obra_completa.txt`. In the recorded notebook run it contains 10,977,812 characters, split sequentially into 90% training data and 10% validation data.

To download the [Machado de Assis dataset from Kaggle](https://www.kaggle.com/datasets/luxedo/machado-de-assis) and rebuild both the consolidated corpus and the individual work files, run:

```bash
python scripts/machado.py
```

You can also build from an existing download without making a network request:

```bash
python scripts/machado.py --zip /path/to/machado-de-assis.zip
```

Use `--saida` and `--obras-dir` to choose custom output locations. The builder validates the expected number of works in every category before writing the corpus.

## Training and generation

The main workflow lives in `train.ipynb`:

1. Define the character vocabulary and encode the corpus.
2. Build random next-character training batches.
3. Initialize the causal Transformer.
4. Train with AdamW, warmup, and cosine learning-rate decay.
5. Save the trained model as a pickle checkpoint.
6. Generate continuations from Machado de Assis quotations or a blank prompt.

Generation behavior can be adjusted with:

- `temperature`: lower values make output more conservative; higher values increase variety.
- `top_k`: restricts sampling to the most likely next characters.
- `max_new_tokens`: controls the generated continuation length.

The included notebook output records a validation loss of `1.3441` at step 12,400. Results will vary because the notebook does not fix random seeds.

## Repository layout

```text
.
├── data/
│   └── machado_de_assis_obra_completa.txt
├── scripts/
│   ├── machado.py       # Downloads, validates, and assembles the corpus
│   └── vocab.py         # Prints the corpus character set
├── train.ipynb          # Model, training loop, and generation examples
├── model-01.pkl         # Experimental trained checkpoint
├── model-{localtime}.pkl
└── requirements.txt
```

## Notes

- This is a learning project, not a production language model. Generated text may be incoherent, repetitive, or factually incorrect.
- The model learns statistical patterns from Machado de Assis's writing; generated passages are not authentic works by the author.
- Python pickle files can execute code while loading. Only load checkpoints you trust.
- Check the source dataset's terms before redistributing or using the corpus beyond this experiment.

## Acknowledgments

The training text comes from the [Machado de Assis dataset published on Kaggle](https://www.kaggle.com/datasets/luxedo/machado-de-assis). The model architecture follows the decoder-only Transformer/GPT family and is implemented for study and experimentation.
