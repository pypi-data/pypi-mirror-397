import argparse
import sys
from . import __version__

def _resolve_pipeline():
    # 1) report.generate_report(input|df, output)
    try:
        from .report import generate_report
        return generate_report
    except Exception:
        pass

    # 2) core.generate_report(input|df, output)
    try:
        from .core import generate_report  # type: ignore
        return generate_report  # type: ignore
    except Exception:
        pass

    # 3) core.run(input|df, output)
    try:
        from .core import run  # type: ignore
        return run  # type: ignore
    except Exception:
        pass

    # 4) core.run_analysis(input|df, output)
    try:
        from .core import run_analysis  # type: ignore
        return run_analysis  # type: ignore
    except Exception:
        pass

    raise ImportError(
        "Impossibile trovare una funzione di pipeline. "
        "Attese una di: report.generate_report, core.generate_report, core.run, core.run_analysis"
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dovalens",
        description="DovaLens — Automated dataset analyzer"
    )
    p.add_argument("--version", action="version", version=f"dovalens {__version__}")
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "--output",
        default="./report.html",
        help="Output HTML report path (default: ./report.html)"
    )
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        pipeline = _resolve_pipeline()
    except ImportError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    # 1) tenta chiamata stile (path, output)
    try:
        pipeline(args.input, args.output)
        return
    except Exception as e1:
        # Se la funzione vuole un DataFrame, riprova caricando il CSV
        try:
            import pandas as pd
            df = pd.read_csv(args.input)
            pipeline(df, args.output)
            return
        except Exception as e2:
            print("Errore nell'esecuzione della pipeline.", file=sys.stderr)
            print(f"Primo tentativo (path, output) -> {type(e1).__name__}: {e1}", file=sys.stderr)
            print(f"Secondo tentativo (DataFrame, output) -> {type(e2).__name__}: {e2}", file=sys.stderr)
            sys.exit(1)
