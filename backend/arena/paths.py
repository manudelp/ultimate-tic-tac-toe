"""Locations that stay out of git."""
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
UTTTAI_ROOT = REPO_ROOT / "third_party" / "utttai"
NMCTS2_WEIGHTS = REPO_ROOT / "backend" / "weights" / "nmcts2.pt"
NMCTS2_ONNX = REPO_ROOT / "backend" / "weights" / "policy_value_net_stage2.onnx"
NMCTS2_ONNX_URL = "https://uttt.ai/policy_value_net_stage2.onnx"
STAGE2_DATASET = REPO_ROOT / "backend" / "datasets" / "stage2-nmcts"
RUNS_DIR = REPO_ROOT / "backend" / "runs"

# Public artifacts from https://github.com/arnowaczynski/utttai (Apache-2.0).
DATASETS_URL = "https://drive.google.com/drive/folders/10JGsynB3Sk8jAMNyIU0xW7nhEArX9xyN"
WEIGHTS_URL = "https://drive.google.com/drive/folders/10VBarorReiesCd0R-r9hhMfXL6MtCNdG"
