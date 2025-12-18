# Jelka Simulation

Simulation for running Jelka FMF patterns.

## Note

If you want to contribute your own Jelka FMF patterns, you should check out the [Storži](https://github.com/Jelka-FMF/Storzi) repository for full instructions about developing and contributing patterns.

## Installation

```sh
pip install jelkasim
```

## Usage

```
usage: jelkasim [-h] [--positions POSITIONS] [runner] target

Run Jelka FMF simulation.

positional arguments:
  runner                  How to run your program.
  target                  Your program name.

options:
  -h, --help              Show this help message and exit.
  --positions POSITIONS   File with LED positions. Leave empty for automatic detection or random.
```

Examples:

```sh
jelkasim moj_vzorec.py
jelkasim moj_vzorec.exe
jelkasim node moj_vzorec.js
jelkasim ocaml moj_vzorec.ml
```

For OCaml inside Docker, something like this should be used (probably):

```sh
jelkasim docker exec container-name "ocaml moj_vzorec.ml"
```

You should also figure out the container name using:

```sh
docker ps
```
