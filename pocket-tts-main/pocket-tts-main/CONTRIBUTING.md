# Contributing to Kyutai Pocket TTS
 
We welcome contributions from the community!

We recommend using `uv` to work on this project. While you can use `pip` too, `uv` is less error-prone and faster.
The instructions below assume you are using `uv`.

## Installing the pre-commit

```bash
uvx pre-commit install
```
This will handle file formatting and linting.

If you want to manually run the pre-commit hooks on all files, use:
```bash
uvx pre-commit run --all-files
```

## Running tests

```bash
uv run pytest -n 3 -v
```
This will run the test suite with 3 parallel workers.

## Running the CLI locally

You can run the CLI commands with:

```bash
uv run pocket-tts generate
```

## Coding agents
We use `AGENTS.md` to manage the coding agents context. If your coding agent does
not supports reading from this file directly, you can just
use a symlink. The most common ones are already added in the `.gitignore` file.

```bash
ln -s AGENTS.md CLAUDE.md
# or
ln -s AGENTS.md QWEN.md
```

## How does this model work?

Here is a high-level overview of the architecture:

![Architecture Diagram](./docs/model_arch.png)

Overall the model has four main components:
* The mimi vae encoder, to encode the audio prompts into a latent representation.
* The text "encoder" which is just a simple tokenizer + embedding layer.
* The calm model (`flow_lm` in the codebase) to generate autoregegressive the audio latents.
* The mimi vae decoder to decode the audio latents into waveform.

Note that two threads run in parallel in the current implementation:
* One with the calm model generating the latents.
* One with the mimi vae decoder decoding the latents into audio.
