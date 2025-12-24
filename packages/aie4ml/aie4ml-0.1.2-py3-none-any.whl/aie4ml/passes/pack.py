# Copyright 2025 D. Danopoulos, aie4ml
# SPDX-License-Identifier: Apache-2.0

"""Pass to pack kernel artifacts into tiled layouts for AIE mmul kernels."""

import numpy as np
from hls4ml.model.optimizer.optimizer import ModelOptimizerPass

from ..ir import get_backend_context


def pack_mmul_rhs_matrix(
    W,
    *,
    K: int,
    N: int,
    K_slice: int,
    N_slice: int,
    tile_k: int,
    tile_n: int,
    cas_length: int,
    cas_num: int,
    order: str = 'C',
    dtype=None,
):
    assert tile_k > 0 and tile_n > 0
    assert K_slice % tile_k == 0
    assert N_slice % tile_n == 0

    W = np.asarray(W)
    if dtype is not None:
        W = W.astype(dtype, copy=False)
    if W.ndim < 2:
        raise ValueError('W must have at least 2 dimensions')
    W_kn = W.reshape((-1, K, N))[-1]

    tiles_per_k = K_slice // tile_k
    tiles_per_n = N_slice // tile_n
    elements_per_tile = tile_k * tile_n
    flat_len = tiles_per_k * tiles_per_n * elements_per_tile

    packed = np.zeros((cas_num, cas_length, flat_len), dtype=W_kn.dtype)
    tile_buf = np.zeros((tile_k, tile_n), dtype=W_kn.dtype)

    for chain in range(cas_num):
        n_base = chain * N_slice
        for cas in range(cas_length):
            flat = packed[chain, cas]
            tile_idx = 0
            for k_tile in range(tiles_per_k):
                gk = cas * K_slice + k_tile * tile_k
                real_k = max(0, min(tile_k, K - gk))
                for n_tile in range(tiles_per_n):
                    tile_buf.fill(0)
                    gn = n_base + n_tile * tile_n
                    real_n = max(0, min(tile_n, N - gn))
                    if real_k > 0 and real_n > 0:
                        tile_buf[:real_k, :real_n] = W_kn[gk : gk + real_k, gn : gn + real_n]
                    start = tile_idx * elements_per_tile
                    flat[start : start + elements_per_tile] = tile_buf.ravel(order=order)
                    tile_idx += 1

    return packed


def pack_vector_by_n_slice(
    v,
    *,
    N: int,
    N_slice: int,
    cas_num: int,
    dtype=None,
):
    v = np.asarray(v)
    if dtype is not None:
        v = v.astype(dtype, copy=False)
    if v.ndim > 1:
        v = v.reshape((-1,))[:N]
    if v.shape[0] != N:
        raise ValueError(f'Vector length mismatch: got {v.shape[0]}, expected {N}')

    packed = np.zeros((cas_num, N_slice), dtype=v.dtype)
    for chain in range(cas_num):
        n_base = chain * N_slice
        real = max(0, min(N_slice, N - n_base))
        if real > 0:
            packed[chain, :real] = v[n_base : n_base + real]
    return packed


class PackKernelArtifacts(ModelOptimizerPass):
    """
    Packs kernel-resident tensors into variant-specific tiled layouts
    required by AIE mmul-based kernels.
    """

    def __init__(self):
        self.name = 'pack_kernel_artifacts'

    def transform(self, model):
        ctx = get_backend_context(model)
        changed = False

        for inst in ctx.ir.kernels:
            attrs = inst.attributes
            pack_key = attrs.pack.get('key')
            if not pack_key:
                continue

            # Cache hit
            if inst.artifacts.get('pack_key') == pack_key:
                continue

            variant = inst.variant
            if not hasattr(variant, 'pack'):
                continue

            packed = variant.pack(inst)

            if packed:
                inst.artifacts.update(packed)
                inst.artifacts['pack_key'] = pack_key
                changed = True

        return changed
