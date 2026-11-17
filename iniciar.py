"""Entrada local: python iniciar.py [--port 8000]."""
import argparse
from backend.server import serve

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Portfolio IA local")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Escolha uma porta entre 1024 e 65535.")
    serve(args.port)
