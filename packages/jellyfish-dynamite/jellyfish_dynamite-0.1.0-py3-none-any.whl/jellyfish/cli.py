# /jellyfish/cli.py

import argparse
from pathlib import Path


# FROM TRANCHE
def add_tranche_parser(subparsers):
    """Add tranche subcommand to jellyfish CLI."""
    parser = subparsers.add_parser('tranche', help='Audio annotation slicing')
    parser.add_argument('audio_dir', help='Directory containing audio files')
    parser.add_argument('annotation_dir', help='Directory containing annotation files')
    parser.add_argument('format', choices=['raven', 'avianz', 'audacity', 'excel'],
                       help='Annotation format')
    parser.add_argument('--base-dir', type=str, default=None,
                       help='Base directory for tranche structure (default: ./tranche)')
    parser.add_argument('--dataset-name', type=str, default="dataset",
                       help='Name for this dataset')
    parser.set_defaults(func=run_tranche)

def run_tranche(args):
    """Execute tranche command."""
    from .tranche import tranche
    
    results = tranche(
        input_audio_directory=args.audio_dir,
        annotation_directory=args.annotation_dir,
        annotation_style=args.format,
        dataset_name=args.dataset_name,
        base_dir=args.base_dir
    )


def main():
    """Command line interface for jellyfish tools."""
    parser = argparse.ArgumentParser(description="Jellyfish Audio Tools")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add tranche subcommand
    add_tranche_parser(subparsers)
    
    # Add other existing subcommands here
    # add_tracer_parser(subparsers)  # template
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    # Execute the selected command
    args.func(args)

if __name__ == "__main__":
    main()


# Usage 1:
# python -m anvo.jellyfish tranche /audio /annotations avianz

# Usage 2: 
# import anvo
# anvo.jellyfish.tranche('/audio', '/annotations', 'raven')
