import argparse
import os
import sys
try:
    from .pipeline import preprocess_and_save
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from vtissue.preprocessing.pipeline import preprocess_and_save

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs="+", required=True)
    parser.add_argument("--gene-list", default=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'human_genome_GRCh38.p14.txt')))
    parser.add_argument("--output", default=None)
    parser.add_argument("--input-layer", default=None)
    parser.add_argument("--norm-method", default=None)
    parser.add_argument("--cofactor", type=float, default=5.0)
    parser.add_argument("--skip-mapping", action="store_true")
    args = parser.parse_args()
    print(f"Inputs: {len(args.input)}")
    print(f"Gene list: {args.gene_list}")
    out = args.output
    if out is None:
        first = args.input[0]
        in_dir = os.path.dirname(os.path.abspath(first))
        base = os.path.splitext(os.path.basename(first))[0]
        name = f"{base}_preprocessed.h5ad" if len(args.input) == 1 else "combined_preprocessed.h5ad"
        out = os.path.join(in_dir, name)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    print(f"Output: {out}")
    print(f"Input layer: {args.input_layer}")
    print(f"Normalization: {args.norm_method}")
    print(f"Skip mapping: {args.skip_mapping}")
    path = preprocess_and_save(
        inputs=args.input,
        gene_list_path=args.gene_list,
        output_path=out,
        input_layer=args.input_layer,
        normalization_method=args.norm_method,
        normalization_cofactor=args.cofactor,
        skip_mapping=bool(args.skip_mapping)
    )
    print(path)

if __name__ == "__main__":
    main()
