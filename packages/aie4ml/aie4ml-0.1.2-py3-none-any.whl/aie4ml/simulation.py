# Copyright 2025 D. Danopoulos, aie4ml
# SPDX-License-Identifier: Apache-2.0

import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Union

import numpy as np

from .aie_types import RoundingMode, SaturationMode
from .ir import get_backend_context
from .passes.quant import apply_rounding, dtype_for_precision, handle_overflow

log = logging.getLogger(__name__)


def read_aie_report(model_or_path: Union[object, str, Path]) -> Dict:
    model = None
    if hasattr(model_or_path, 'config'):
        model = model_or_path
        output_dir = Path(model.config.get_output_dir())
    else:
        output_dir = Path(model_or_path)
    output_dir = output_dir.resolve()

    ii_info = _analyze_aie_out_interval(output_dir)
    graph_info = _read_aie_graph_stats(output_dir)
    report = {}

    global_ii = ii_info.get('global', {})
    if global_ii and model is not None:
        ops_per_inf = compute_ops(model)
        batch_size = model.config.get_config_value('AIEConfig')['BatchSize']
        total_ops = ops_per_inf * batch_size
        report['throughput'] = {
            'Avg_GOPs': round((total_ops / global_ii['avg_ns']), 3),
            'Min_GOPs': round((total_ops / global_ii['min_ns']), 3),
            'Max_GOPs': round((total_ops / global_ii['max_ns']), 3),
        }

    report['output_interval'] = ii_info
    report['AIE_info'] = graph_info

    return report


def _read_aie_graph_stats(output_dir: Path) -> Dict:
    report_path = output_dir / 'Work' / 'reports' / 'app_mapping_analysis_report.txt'

    if report_path.exists():
        try:
            with open(report_path) as f:
                text = f.read().strip('\n')
            return text.splitlines()
        except Exception as e:
            return f'error Failed to read AIE graph report: {e} in {str(report_path)}'

    return 'No AIE graph report found. Run AIE hardware compilation to generate it.'


def _analyze_aie_out_interval(output_dir: Path) -> Dict:
    data_dir = output_dir / 'aiesimulator_output' / 'data'

    if not data_dir.exists():
        return {}

    per_file = {}
    all_lat = []

    for fp in sorted(data_dir.glob('y_p*.txt')):
        lst = _parse_timing(fp)
        if lst:
            per_file[fp.name] = {
                'min_ns': round(min(lst), 3),
                'max_ns': round(max(lst), 3),
                'avg_ns': round(sum(lst) / len(lst), 3),
                'samples': len(lst),
            }
            all_lat.extend(lst)

    if not all_lat:
        return {}

    return {
        'global': {
            'min_ns': round(min(all_lat), 3),
            'max_ns': round(max(all_lat), 3),
            'avg_ns': round(sum(all_lat) / len(all_lat), 3),
            'samples': len(all_lat),
        },
        'per_port': per_file,
    }


def _parse_timing(path: Path) -> List[float]:
    """Return TLAST-to-TLAST intervals (in nanoseconds)."""
    regex = re.compile(r'^T\s+(\d+)\s*(ps|ns|us|ms|s)', re.IGNORECASE)

    lat = []
    last_tlast_time = None
    current_time = None

    with open(path) as f:
        for line in f:
            line = line.strip()

            m = regex.match(line)
            if m:
                val, unit = m.groups()
                current_time = _convert_to_ns(int(val), unit)
                continue

            if 'TLAST' in line.upper():
                if last_tlast_time is not None and current_time is not None:
                    dt = current_time - last_tlast_time
                    if dt >= 0:
                        lat.append(dt)
                last_tlast_time = current_time

    return lat


def _convert_to_ns(value: int, unit: str) -> float:
    if unit == 'ps':
        return value / 1000
    if unit == 'ns':
        return value
    if unit == 'us':
        return value * 1000
    if unit == 'ms':
        return value * 1_000_000
    if unit == 's':
        return value * 1_000_000_000
    raise ValueError(f'Unknown time unit: {unit}')


def compute_ops(model):
    ctx = get_backend_context(model)
    ops = 0
    for node in ctx.ir.logical:
        if node.op_type == 'dense':
            n_in = int(node.metadata.get('n_in', 0))
            n_out = int(node.metadata.get('n_out', 0))
            ops += 2 * n_in * n_out
    return ops


@dataclass
class LayerIOInfo:
    cas_length: int
    cas_num: int
    in_features: int
    out_features: int
    in_feat_slice: int
    out_feat_slice: int
    raw_in_feat_slice: int
    raw_out_feat_slice: int
    padded_in_features: int
    padded_out_features: int
    input_bitwidth: int
    output_bitwidth: int
    input_fractional_bits: int = 0
    output_fractional_bits: int = 0
    input_rounding_mode: RoundingMode = RoundingMode.RND
    input_saturation_mode: SaturationMode = SaturationMode.SAT
    input_signed: bool = True
    output_signed: bool = True


def extract_dense_io(model):
    ctx = get_backend_context(model)
    dense_nodes = [node for node in ctx.ir.logical if node.op_type == 'dense']
    if not dense_nodes:
        raise RuntimeError('AIE simulation requires at least one Dense node to describe IO slicing.')

    def _rounding_from_spec(spec_rounding) -> RoundingMode:
        if isinstance(spec_rounding, RoundingMode):
            return spec_rounding
        if isinstance(spec_rounding, str):
            return RoundingMode[spec_rounding]
        raise TypeError(f'Unsupported rounding mode representation: {type(spec_rounding)}')

    def _saturation_from_spec(spec_saturation) -> SaturationMode:
        if isinstance(spec_saturation, SaturationMode):
            return spec_saturation
        if isinstance(spec_saturation, str):
            return SaturationMode[spec_saturation]
        raise TypeError(f'Unsupported saturation mode representation: {type(spec_saturation)}')

    def _info(node):
        inst = ctx.ir.kernels.get(node.name)
        if inst is None:
            raise RuntimeError(f'{node.name}: unresolved IR node. Run resolve pass first.')

        attrs = inst.attributes
        metadata = node.metadata or {}
        in_features = int(metadata['n_in'])
        out_features = int(metadata['n_out'])
        parallel = attrs.parallelism
        cas_length = int(parallel['cas_length'])
        cas_num = int(parallel['cas_num'])
        slices = attrs.slices
        raw_in_slice = int(slices['input_raw'])
        raw_out_slice = int(slices['output_raw'])
        in_slice = int(slices['input'])
        out_slice = int(slices['output'])
        numeric = attrs.numeric
        input_spec = numeric['input']
        output_spec = numeric['output']

        input_bw = int(getattr(input_spec, 'width'))
        output_bw = int(getattr(output_spec, 'width'))
        input_frac = int(getattr(input_spec, 'frac', getattr(input_spec, 'fractional', 0)) or 0)
        output_frac = int(getattr(output_spec, 'frac', getattr(output_spec, 'fractional', 0)) or 0)

        rounding_mode = _rounding_from_spec(getattr(input_spec, 'rounding'))
        saturation_mode = _saturation_from_spec(getattr(input_spec, 'saturation'))

        signed_inputs = bool(getattr(input_spec, 'signed'))
        signed_outputs = bool(getattr(output_spec, 'signed'))

        scalars = attrs.scalars
        padded_in_features = int(scalars['padded_in_features'])
        padded_out_features = int(scalars['padded_out_features'])

        return LayerIOInfo(
            cas_length=cas_length,
            cas_num=cas_num,
            in_features=in_features,
            out_features=out_features,
            in_feat_slice=in_slice,
            out_feat_slice=out_slice,
            raw_in_feat_slice=raw_in_slice,
            raw_out_feat_slice=raw_out_slice,
            padded_in_features=padded_in_features,
            padded_out_features=padded_out_features,
            input_bitwidth=input_bw,
            output_bitwidth=output_bw,
            input_fractional_bits=input_frac,
            output_fractional_bits=output_frac,
            input_rounding_mode=rounding_mode,
            input_saturation_mode=saturation_mode,
            input_signed=signed_inputs,
            output_signed=signed_outputs,
        )

    return _info(dense_nodes[0]), _info(dense_nodes[-1])


def prepare_input_tensor(model, X, io_info, batch_size, iterations, quantize_inputs=True):
    if X is None:
        raise ValueError('Input data is required for AIE simulation.')

    input_vars = model.get_input_variables()
    if len(input_vars) != 1:
        raise NotImplementedError('AIE simulation currently supports single-input models only.')

    expected_size = input_vars[0].size()

    data = np.asarray(X)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    if data.ndim == 2:
        if data.shape[0] != batch_size:
            raise ValueError(
                f'Input batch dimension ({data.shape[0]}) does not match configured BatchSize ({batch_size}).'
            )
        if data.shape[1] != expected_size:
            raise ValueError(
                f'Input feature dimension ({data.shape[1]}) does not match expected size ({expected_size}).'
            )
        data = np.repeat(data[np.newaxis, :, :], iterations, axis=0)
    elif data.ndim == 3:
        if data.shape[2] != expected_size:
            raise ValueError(
                f'Input feature dimension ({data.shape[2]}) does not match expected size ({expected_size}).'
            )
        if data.shape[1] != batch_size:
            raise ValueError(
                f'Provided batch dimension ({data.shape[1]}) does not match configured BatchSize ({batch_size}).'
            )
        if data.shape[0] != iterations:
            raise ValueError(
                f'Input iteration dimension ({data.shape[0]}) does not match configured Iterations ({iterations}).'
            )
    else:
        raise ValueError(
            'Expected input array with shape [batch_size, features] or [iterations, batch_size, features]; '
            f'got shape {data.shape}.'
        )

    padded_feat = io_info.cas_length * io_info.in_feat_slice
    if padded_feat == io_info.in_features:
        padded = data
    else:
        padded = np.zeros((iterations, batch_size, padded_feat), dtype=data.dtype)
        padded[:, :, : io_info.in_features] = data

    if quantize_inputs:
        processed = _quantize_inputs_to_int(padded, io_info)
    else:
        if not np.issubdtype(padded.dtype, np.integer):
            raise ValueError(
                'Non-integer inputs require quantize_inputs=True or manual quantization before prediction.'
            )
        target_dtype = dtype_for_precision(io_info.input_bitwidth, io_info.input_signed)
        processed = padded.astype(target_dtype, copy=False)

    return np.ascontiguousarray(processed)


def write_input_files(output_dir, inputs, io_info, vals_per_line):
    data_dir = Path(output_dir) / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)

    slice_size = io_info.raw_in_feat_slice
    for col in range(io_info.cas_length):
        file_path = data_dir / f'ifm_c{col}.txt'
        with open(file_path, 'w') as handle:
            start = col * slice_size
            values = inputs[:, :, start : start + slice_size]
            _write_values(handle, values.flatten(order='C'), vals_per_line)


def write_numpy_outputs(output_dir, np_outputs, io_info, batch_size, iterations, vals_per_line):
    """
    Write NumPy emulation outputs into output_dir/data/y_p{i}.txt, matching the simulator's format.
    """
    data_dir = Path(output_dir) / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)

    total_out = io_info.cas_num * io_info.raw_out_feat_slice

    arr = np.asarray(np_outputs)
    if arr.ndim == 2:
        if arr.shape[0] != iterations * batch_size or arr.shape[1] < total_out:
            raise ValueError(
                f'np_outputs shape {arr.shape} does not match expected '
                f'[(iterations*batch)={iterations*batch_size}, total_out={total_out}]'
            )
        arr = arr[:, :total_out].reshape(iterations, batch_size, total_out)
    elif arr.ndim == 3:
        if arr.shape[:2] != (iterations, batch_size) or arr.shape[2] < total_out:
            raise ValueError(
                f'np_outputs shape {arr.shape} does not match expected '
                f'[{iterations}, {batch_size}, total_out>={total_out}]'
            )
        arr = arr[:, :, :total_out]
    else:
        raise ValueError(f'Unsupported np_outputs ndim {arr.ndim}')

    for i in range(io_info.cas_num):
        file_path = data_dir / f'y_p{i}.txt'
        with open(file_path, 'w') as f:
            out_slice = arr[:, :, i * io_info.raw_out_feat_slice : (i + 1) * io_info.raw_out_feat_slice]
            _write_values(f, out_slice.flatten(order='C'), vals_per_line)


def _write_values(stream, values, vals_per_line):
    if vals_per_line <= 0:
        vals_per_line = len(values)

    for idx, value in enumerate(values):
        if idx and idx % vals_per_line == 0:
            stream.write('\n')
        elif idx:
            stream.write(' ')
        stream.write(str(int(value)))

    stream.write('\n')


def collect_outputs(output_dir, sim_mode, io_info, batch_size, iterations):
    data_dir = Path(output_dir) / f'{sim_mode}simulator_output/data'
    outputs = np.zeros(
        (iterations, batch_size, io_info.cas_num * io_info.raw_out_feat_slice),
        dtype=np.int32,
    )

    expected_values = iterations * batch_size * io_info.raw_out_feat_slice
    for chain in range(io_info.cas_num):
        file_path = data_dir / f'y_p{chain}.txt'
        if not file_path.exists():
            raise FileNotFoundError(f'Expected simulator output {file_path} not found.')

        with open(file_path, 'r') as handle:
            tokens = handle.read().split()

        if not tokens:
            raise RuntimeError(f'Output file {file_path} is empty.')

        # filter out non data markers
        clean_tokens = []
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok.upper() == 'TLAST':
                i += 1
                continue
            if tok.upper() == 'T' and i + 2 < len(tokens):
                i += 3
                continue
            clean_tokens.append(tok)
            i += 1
        values = np.array([int(t) for t in clean_tokens], dtype=np.int32)

        if values.size < expected_values:
            raise RuntimeError(
                f'Output file {file_path} contained {values.size} values; expected at least {expected_values}.'
            )

        reshaped = values[:expected_values].reshape(iterations, batch_size, io_info.raw_out_feat_slice)
        start = chain * io_info.raw_out_feat_slice
        outputs[:, :, start : start + io_info.raw_out_feat_slice] = reshaped

    flattened = outputs.reshape(iterations * batch_size, io_info.cas_num * io_info.raw_out_feat_slice)
    if flattened.shape[0] == 1:
        return flattened[0]

    return flattened


def dequantize_outputs(data: np.ndarray, io_info: LayerIOInfo) -> np.ndarray:
    fractional_bits = max(0, io_info.output_fractional_bits)
    if fractional_bits == 0:
        return data.astype(np.float64, copy=False)

    scale = float(1 << fractional_bits)
    return data.astype(np.float64, copy=False) / scale


def numpy_emulate(model, prepared_inputs):
    """NumPy emulation of AIE Dense nodes using quantized IR artifacts."""
    ctx = get_backend_context(model)
    dense_nodes = [node for node in ctx.ir.logical if node.op_type == 'dense']
    if not dense_nodes:
        raise RuntimeError('AIE numpy emulation requires at least one Dense node.')

    first_layer, _ = extract_dense_io(model)
    aie_cfg = model.config.get_config_value('AIEConfig', {}) or {}
    batch_size = int(aie_cfg.get('BatchSize'))
    iterations = int(aie_cfg.get('Iterations'))

    # Trim to true feature count and flatten [iters*batch, in_features]
    X = prepared_inputs[:, :, : first_layer.in_features]
    X = X.reshape(iterations * batch_size, first_layer.in_features).astype(np.int64, copy=False)

    for node in dense_nodes:
        inst = ctx.ir.kernels.get(node.name)
        if inst is None:
            raise RuntimeError(f'{node.name}: unresolved IR node. Run resolve pass first.')

        attrs = inst.attributes
        if 'quant' not in node.metadata:
            raise RuntimeError(f'{node.name}: missing quant metadata; run quantization pass first.')
        quant_meta = node.metadata['quant']
        if not isinstance(quant_meta, dict):
            raise TypeError(f'{node.name}: quant metadata must be a dict, got {type(quant_meta)}')

        W = node.artifacts.get('quant_weights')
        if W is None:
            raise RuntimeError(f'{node.name}: quantized weights missing. Run quantization pass first.')
        W = np.asarray(W, dtype=np.int64)

        b = node.artifacts.get('quant_bias')
        shift = int(attrs.scalars['shift'])
        use_bias = bool(node.metadata.get('use_bias')) and b is not None
        use_relu = bool(attrs.flags.get('use_relu', False))

        output_spec = attrs.numeric.get('output')
        out_bw = int(getattr(output_spec, 'width', 8) or 8)
        out_signed = bool(getattr(output_spec, 'signed', True))

        if 'output_precision' not in quant_meta:
            raise RuntimeError(f'{node.name}: missing quant intent "output_precision"')
        output_precision = quant_meta['output_precision']
        out_rounding_mode = output_precision.rounding
        out_saturation_mode = output_precision.saturation

        acc = X @ W
        if use_bias:
            acc += np.asarray(b, dtype=np.int64)

        if shift != 0:
            acc = _requantize_int(acc, shift, out_rounding_mode)

        acc = handle_overflow(acc, out_bw, out_signed, out_saturation_mode)

        if use_relu:
            acc = np.maximum(acc, 0)

        out_dtype = dtype_for_precision(out_bw, out_signed)
        X = acc.astype(out_dtype, copy=False)

    return X


def _requantize_int(acc: np.ndarray, shift: int, rounding_mode: RoundingMode) -> np.ndarray:
    """Integer requantization: right shift with symmetric rounding; left shift exact."""
    acc = acc.astype(np.int64, copy=False)
    if shift == 0:
        return acc
    if shift < 0:
        return acc << (-shift)

    s = int(shift)
    if rounding_mode == RoundingMode.RND:
        bias = 1 << (s - 1)
        pos = (acc + bias) >> s
        neg = -(((-acc) + bias) >> s)
        return np.where(acc >= 0, pos, neg)

    scale = float(1 << s)
    rounded = apply_rounding(acc.astype(np.float64) / scale, rounding_mode)
    return rounded.astype(np.int64, copy=False)


def _quantize_inputs_to_int(data, io_info):
    if np.issubdtype(data.dtype, np.integer):
        target_dtype = dtype_for_precision(io_info.input_bitwidth, io_info.input_signed)
        return data.astype(target_dtype, copy=False)

    width = io_info.input_bitwidth
    fractional_bits = max(0, io_info.input_fractional_bits)
    scale = 1 << fractional_bits if fractional_bits > 0 else 1
    scaled = data * scale

    rounded = apply_rounding(scaled, io_info.input_rounding_mode)
    integers = rounded.astype(np.int64)

    processed = handle_overflow(integers, width, io_info.input_signed, io_info.input_saturation_mode)
    target_dtype = dtype_for_precision(width, io_info.input_signed)
    return processed.astype(target_dtype, copy=False)


def run_simulation_target(output_dir, make_target):
    cmd = ['make', make_target]
    result = subprocess.run(cmd, cwd=Path(output_dir), text=True)
    if result.returncode != 0:
        raise RuntimeError(f'Make target "{make_target}" failed in {output_dir}.')
