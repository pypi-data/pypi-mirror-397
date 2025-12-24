import os
import numpy as np
import torch
from tqdm import tqdm
from torch.utils.cpp_extension import load
import torch as th

# ─────────── build / load the CUDA extension ────────────
def _load_xbit_ext():
    os.environ.setdefault("TORCH_CUDA_ARCH_LIST", "8.9")   # change if needed
    return load(
        name="xbit_cuda",
        sources=["xbit_bind.cpp", "xbit.cu"],
        extra_cuda_cflags=["-O3", "--use_fast_math"],
        extra_cflags=["-O3"],
        verbose=False,
        #is_standalone=True,
        #is_python_module=False,
    )

# ─────────── constants ───────────────────────────────────
MAX_SYMBOLS_KERNEL = 100_000_000                 # 1e8 symbols  ~100 MiB
BYTES_KERNEL       = MAX_SYMBOLS_KERNEL          # uint8 ⇒ same #bytes

# ─────────── main helper ─────────────────────────────────
def compress_seq_only(
    tsv_in: str,
    xbit_out: str,
    *,
    outer_bytes: int = 1 << 30,     # ≈1 GiB of raw TSV
    verify: bool     = True,        # round-trip each outer chunk
    max_chunks: int | None = None,  # e.g. 1 for a quick test
):
    xbit  = _load_xbit_ext()
    fout  = open(xbit_out, "wb")

    seq_buf = bytearray()        # accumulates "SEQ@SEQ@…" up to outer_bytes
    bytes_in_outer = 0
    outer_idx = 0
    c = 0
    skips_X = 0
    skips_len = 0
    ok_seqs = 0 

    with open(tsv_in, "rb") as fin:
        total_size = os.path.getsize(tsv_in)
        print(total_size, tsv_in)
        pbar = tqdm(unit="B", unit_scale=True, desc="Compressing", total=total_size)
        for line in fin:
            c+=1
            # -------- strip integers, keep sequence ----------
            #parts = line.split(b'\t', 1)
            #if len(parts) < 2:
            #    continue                       # malformed line
            #seq = parts[1].rstrip(b'\n')
            seq = line.rstrip(b'\n')#.rstrip(b'X') # remove all X's?
            if b'X' in seq or b'x' in seq: 
                skips_X+=1
                if skips_X % 100000 == 0:
                    pbar.set_postfix(skipX=skips_X, skipLen=skips_len, ok=ok_seqs)
                pbar.update(len(line))
                seq = seq.replace(b'X', b'S').replace(b'x', b'S')

                #continue  # skip sequences with X'''
            if len(seq) > 1024:
                skips_len+=1
                if skips_len % 100000 == 0:
                    pbar.set_postfix(skipX=skips_X, skipLen=skips_len, ok=ok_seqs)
                pbar.update(len(line))
                continue
            seq_buf.extend(seq + b'@')         # append delim
            ok_seqs += 1

            bytes_in_outer += len(seq) + 1
            pbar.update(len(line))
            if ok_seqs % 100000 == 0:
                pbar.set_postfix(skipX=skips_X, skipLen=skips_len, ok=ok_seqs)
            #if c % 1000000: print(len(seq))

            #print(line)
            #if c == 10: return

            # ---------- hit 1 GiB?  compress+verify ----------
            if bytes_in_outer >= outer_bytes:
                _encode_outer(seq_buf, xbit, fout, verify, outer_idx)
                seq_buf.clear()
                bytes_in_outer = 0
                outer_idx += 1

                if max_chunks is not None and outer_idx >= max_chunks:
                    break

        # flush tail
        if seq_buf:
            _encode_outer(seq_buf, xbit, fout, verify, outer_idx)

        pbar.close()
    fout.close()
    print("✅  finished — every outer chunk verified on the fly")

# ─────────── encode & verify one outer buffer ───────────
def _encode_outer(buf, xbit, fout, verify, outer_idx):
    for inner_off in range(0, len(buf), BYTES_KERNEL):
        sub = memoryview(buf)[inner_off : inner_off + BYTES_KERNEL]
        arr = np.frombuffer(sub, dtype=np.uint8).copy()   # writable view
        
        # Pad to multiple of 8 if needed
        if arr.size % 8 != 0:
            pad_size = 8 - (arr.size % 8)
            arr = np.pad(arr, (0, pad_size), mode='constant', constant_values=64)  # pad with '@' chars
        
        tin = torch.from_numpy(arr)
        tcmp = xbit.compress(tin)
        fout.write(tcmp.cpu().numpy().tobytes())

        if verify:
            tout = xbit.decompress(tcmp.cpu(), arr.size).cpu()
            print(tin, tin.shape)
            print(tout, tout.shape)

            if not torch.equal(tout, tin):
                raise RuntimeError(
                    f"Round-trip mismatch in outer {outer_idx}, "
                    f"offset {inner_off//BYTES_KERNEL}"
                )

# ─────────── quick demo / smoke-test ─────────────────────
if __name__ == "__main__":
    #IN  = "/mnt/ssd/mmseqs2/uniref30_2302_seq.tsv"
    #IN  = "../tsv/uniref30_2302_seq_only_len_sorted.tsv"
    #IN  = "../tsv/bfd_mgy_colabfold_seq_only_sorted.tsv"
    #IN  = "/mnt/ssd/sseqs/tsv/uniref30_2302_bfd_mgy_colabfold.tsv"
    #IN = "/mnt/ssd/sseqs/tsv/uniref30_2302_bfd_mgy_colabfold_unique.tsv"
    #OUT = "../xbit/bfd_mgy_colabfold.xbit"
    #OUT = "../xbit/uniref30_2302_bfd_mgy_colabfold.xbit"
    #IN = "/mnt/ssd/sseqs/tsv/uniparc/uniparc_sorted.fasta"
    #OUT = "/mnt/ssd/sseqs/xbit/uniparc_noX.xbit"

    #IN = "/mnt/ssd/sseqs/tsv/bfd/combined_only_seq_sorted.tsv"
    #OUT = "/mnt/ssd/sseqs/xbit/bfd.xbit"

    IN = "/mnt/ssd/sseqs/tsv/envdb/combined_only_seq_sorted.tsv"
    OUT = "/mnt/ssd/sseqs/xbit/envdb.xbit"

    if False: 
        a = th.empty((33554455), dtype=th.uint8, pin_memory=True)

        with open(OUT, "rb") as fh:          # independent preload loop
            fh.readinto(a.numpy()) 

        print(a, a.min(), a.max(), a.shape)
        #exit()

        xbit  = _load_xbit_ext()
        tout = xbit.decompress(a.cpu(), 33554455).cpu()
        print(tout)

    # One-chunk smoke test: finishes in ~10 s instead of 10 min
    compress_seq_only(
        IN, OUT,
        outer_bytes = 1 << 30,   # 1 GiB window
        max_chunks  = None, # 40, #None, # 10, # None,         # stop after first outer chunk
        verify      = False       # decompress+compare right away
    )

    # we can prove that linear_gap=-1 is alwasy <= affine_gap open=11,extend=-1
