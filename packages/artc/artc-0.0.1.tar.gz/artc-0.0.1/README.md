# ARTC - Adaptive Regression Tensor Compression

A family of compression algorithms optimized for different use cases. 

# (WIP - ARTC-LITE 0.1.0 and General ARTC 0.1.0)

## Variants

### ARTC 1.0.0:  General Adaptive Regression Tensor Compression
**For:** Any data, any use case

### ARTC-PREDICT:  General Adaptive Regression Tensor Compression for Prediction
**For:** Based on a EKF to predict future values, and then compresses the error between the prediction and the actual value.
**Benefits:**
- Very High compression on predictable data
- Low RAM usage
- Fast

### ARTC-LITE:  Lightweight IoT Tensor Encoding
**For:** IoT sensors, embedded devices, battery-powered systems

```python
from artc import ARTCLITE

# Temperature sensor example
compressor = ARTCLITE(block_size=8, tolerance=0.1)
compressed = compressor.compress(sensor_data)
compressor.print_stats()
```

**Benefits:**
- 2-10× compression on smooth sensor data
- Minimal RAM usage (~50 bytes)
- Fast (< 1ms per block)
- Easy to port to C/Arduino

### ARTC-VRAM *(Coming Soon)*
**For:** GPU memory compression, fitting bigger AI models

### ARTC - FLEX *(Coming Soon)*
**For:** Formula-based Lightweight Efficient eXtended (memory) - ARTC for AI/MLs for GPUs.

---
VERSION PROGRESSION FOR ARTC:                             
- 0.0.1  (Initial concept)
- 0.0.2  (Proof of concept)
- 0.0.3  (PIP Deployment Alpha)
- 0.0.4  (Beta)
- 0.0.5  (Pre-release)
- 0.0.6  (Release candidate)
- 0.0.7  (Bug fixes)
- 0.0.8  (Optimizations)
- 0.0.9  (Documentation)
- 0.1.0  (ARTC-LITE and General ARTC)
- 1.0.0  (General Adaptive Regression Tensor Compression)
====== 
- 1.1.0  (ARTC Stable Deployment)
---

## Installation

```bash
pip install artc
```

Or install from source:

```bash
git clone https://github.com/169B/artc.git
cd artc
pip install -e .
```

## How It Works

ARTC-LITE finds patterns in smooth data by fitting simple formulas. 

```
Input:  [20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5]  (32 bytes)
Pattern: Goes up by 0.5 each time
Formula: y = 0.5x + 20.0
Stored:   m=0.5, b=20.0  (8 bytes)
Result:  4× smaller
```
COMPRESSION PIPELINE:
────────────────────────────────────────────────────────────────

1. MEMORY FETCH (GPU → CPU or within GPU)
   ├── Read block of data from memory
   ├── Cost: Memory bandwidth limited
   └── Time: ~0.1ms per block

2. COMPUTE REGRESSION 
   ├── Calculate:  Σ(xy), Σ(x²), means, etc.
   ├── Cost: Floating point operations
   └── Time: ~0.01ms per block

3. ERROR CHECKING
   ├── Predict all points:  y = mx + b
   ├── Calculate:  |actual - predicted|
   ├── Find max error
   └── Time: ~0.01ms per block

4. DECISION & ENCODE
   ├── If error < tolerance: store (m,b)
   ├── Else: store raw data
   └── Time: ~0.001ms

5. MEMORY WRITE (back to storage)
   ├── Write compressed data
   └── Time: ~0.05ms

TOTAL PER BLOCK: ~0.17ms


DECOMPRESSION PIPELINE:
────────────────────────────────────────────────────────

1. MEMORY FETCH
   ├── Read compressed data (m, b) or raw
   └── Time: ~0.05ms

2. DECODE
   ├── Check type:  formula or raw? 
   ├── If formula: compute y = m*x + b for all points
   ├── If raw: copy directly
   └── Time: ~0.02ms

3. MEMORY WRITE
   ├── Write decompressed data
   └── Time: ~0.1ms

TOTAL PER BLOCK: ~0.17ms
## Comparison

| Method | Sensor Data | Random Data | Speed | RAM |
|--------|-------------|-------------|-------|-----|
| **ARTC-LITE** | **2-10×** | ~1× | ***~50 bytes** |
| GZIP | 1.1× | 1-2× | Medium | ~32 KB |


## License

GNU Generic 3.0
