import argparse
import torch
from yolox.models import create_yolox_model

parser = argparse.ArgumentParser()
parser.add_argument("--model_name", type=str, default="yolox-s")
parser.add_argument("--checkpoint_path", type=str, default="./YOLOX_outputs/yolox-s/best_ckpt.pth")
parser.add_argument("--output_path", type=str, default="./YOLOX_outputs/yolox-s/best_ckpt.onnx")
parser.add_argument("--input_size", type=int, default=640)
args = parser.parse_args()

model = create_yolox_model(name=args.model_name, num_classes=9)
model.load_state_dict(torch.load(args.checkpoint_path, map_location=torch.device('cpu'), weights_only=False)["model"])
model.eval()

# torch.onnx.export(model, args=torch.randn((1, 3, 416, 416)), f=OUTPUT_PATH)
torch.onnx.export(model, args=torch.randn((1, 3, args.input_size, args.input_size)), f=args.output_path, external_data=False)