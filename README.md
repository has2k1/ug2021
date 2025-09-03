# ug2021

## How to install

1. Make sure you have uv and quarto installed
   - [uv](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)
   - [quarto](https://quarto.org/docs/get-started/)

2. Clone this repository

   ```bash
   git clone https://github.com/has2k1/ug2021
   ```

3. Create and update the project environment

   ```bash
   uv sync
   ```

4. Install `ug2021` package in developer mode

   ```bash
   uv pip install -e .
   ```

## Build the site

Check that everything is okay by building the site.

```bash
cd site
uv run quarto render
```

You can open the `_site/index.html`.

## Do your thing

Anything you put in the `.local` folder will be ignored by git.

```bash
cd .local
```

So that is good place to play around, creating notebooks and quarto sites.

## On invoking `jupyter` or `quarto`

Use `uv run` to invoke any programs that you want to use the environment that you have installed, _provided you are inside the project folder_. For example:

```bash
uv run jupyter notebook
uv run jupyter lab
uv run quarto preview
uv run quarto render
```

