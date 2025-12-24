# Ultralytics YOLO 🚀, AGPL-3.0 license
"""
Simplified exporter module containing only format definitions needed for inference.
"""


def export_formats():
    """Ultralytics YOLO export formats."""
    x = [
        ["PyTorch", "-", ".pt", True, True],
        ["TorchScript", "torchscript", ".torchscript", True, True],
        ["ONNX", "onnx", ".onnx", True, True],
        ["OpenVINO", "openvino", "_openvino_model", True, False],
        ["TensorRT", "engine", ".engine", False, True],
        ["CoreML", "coreml", ".mlpackage", True, False],
        ["TensorFlow SavedModel", "saved_model", "_saved_model", True, True],
        ["TensorFlow GraphDef", "pb", ".pb", True, True],
        ["TensorFlow Lite", "tflite", ".tflite", True, False],
        ["TensorFlow Edge TPU", "edgetpu", "_edgetpu.tflite", True, False],
        ["TensorFlow.js", "tfjs", "_web_model", True, False],
        ["PaddlePaddle", "paddle", "_paddle_model", True, True],
        ["MNN", "mnn", ".mnn", True, True],
        ["NCNN", "ncnn", "_ncnn_model", True, True],
        ["IMX", "imx", "_imx_model", True, True],
    ]
    return dict(zip(["Format", "Argument", "Suffix", "CPU", "GPU"], zip(*x)))


def gd_outputs(gd):
    """TensorFlow GraphDef model output node names."""
    name_list, input_list = [], []
    for node in gd.node:  # tensorflow.core.framework.node_def_pb2.NodeDef
        name_list.append(node.name)
        input_list.extend(node.input)
    return sorted(f"{x}:0" for x in list(set(name_list) - set(input_list)) if not x.startswith("NoOp"))

