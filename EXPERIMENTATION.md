# 🧪 Experimentation Log: Orpheus TTS Model Deployment on QAI Hub

## 📋 Objective
Deploy a full precision 3B parameter Orpheus TTS model (based on LLaMA architecture) on Qualcomm AI Hub for optimized inference on NPU hardware.

## 🎯 Initial Setup
- **Model**: Orpheus TTS 3B (LLaMA-based architecture)
- **Target Platform**: Qualcomm AI Hub with NPU acceleration
- **Desired Precision**: FP32 (Full Precision)
- **Expected Benefits**: Hardware-accelerated TTS inference with natural speech quality

---

## 🔬 Experiment 1: Direct ONNX Conversion

### Approach
Attempted direct conversion of the Orpheus model to ONNX format for QAI Hub deployment.

### Process
```bash
# Direct ONNX export attempt
python convert_to_onnx.py --model orpheus-3b --output orpheus.onnx
```

### Results
❌ **FAILED**

### Issues Encountered
- **Architecture Incompatibility**: Orpheus's custom attention mechanisms not directly supported by ONNX
- **Dynamic Shape Issues**: Variable-length audio sequences caused tensor shape conflicts
- **Custom Operators**: Orpheus-specific audio processing layers not recognized by ONNX converter
- **Memory Layout**: Model's internal tensor arrangements incompatible with standard ONNX format

### Root Cause Analysis
The Orpheus model uses specialized audio processing layers and attention mechanisms that are not part of the standard ONNX operator set, making direct conversion impossible without significant architectural modifications.

---

## 🔬 Experiment 2: QAI Hub FP32 Pipeline

### Approach
Utilized QAI Hub's official FP32 conversion pipeline with proper model preparation and input specification.

### Process
```bash
# QAI Hub conversion pipeline
qai-hub-models convert --model orpheus-3b --precision fp32 --target-device snapdragon-8-gen-3
```

### Initial Issues Encountered

#### 🚨 Input Specification Errors
```
ERROR: Input spec mismatch - expected tensor shape [1, 80, 1024] but got [1, 1024, 80]
ERROR: Config validation failed - audio_features dimension incompatible
```

#### 🔧 Resolution Attempts
1. **Extensive Documentation Research**
   - Studied Orpheus training documentation
   - Analyzed input manifest specifications
   - Reviewed QAI Hub model requirements

2. **Input Specification Modifications**
   ```python
   # Original input spec
   input_spec = {
       'audio_features': [1, 1024, 80],  # [batch, seq_len, features]
       'speaker_embedding': [1, 256]
   }
   
   # Modified input spec after documentation review
   input_spec = {
       'audio_features': [1, 80, 1024],  # [batch, features, seq_len] 
       'speaker_embedding': [1, 256],
       'attention_mask': [1, 1024]  # Added missing attention mask
   }
   ```

3. **Tensor Reshaping Operations**
   ```python
   # Added preprocessing to handle tensor shape mismatches
   def preprocess_inputs(audio_features, speaker_embedding):
       # Transpose audio features to match expected format
       audio_features = audio_features.transpose(1, 2)
       
       # Ensure proper tensor dimensions
       if audio_features.shape[0] != 1:
           audio_features = audio_features.unsqueeze(0)
           
       return audio_features, speaker_embedding
   ```

4. **Configuration File Updates**
   ```yaml
   # Updated model config
   model_config:
     input_shapes:
       audio_features: [1, 80, 1024]
       speaker_embedding: [1, 256]
       attention_mask: [1, 1024]
     output_shapes:
       generated_audio: [1, 22050]  # 1 second at 22kHz
     precision: fp32
     optimization_level: 2
   ```

### Final Conversion Attempt
After extensive modifications and tensor reshaping:

```bash
qai-hub-models convert \
  --model orpheus-3b-modified \
  --precision fp32 \
  --input-spec input_manifest.json \
  --config model_config.yaml \
  --target-device snapdragon-8-gen-3
```

### Results
❌ **FAILED WITH MEMORY ERROR**

### Critical Error
```
ERROR: Out of memory during model compilation
Maximum memory size: 10240MB
Required memory: ~12800MB for FP32 3B parameter model
```

### Analysis
- **Model Size**: 3B parameters × 4 bytes (FP32) = ~12GB base model size
- **QAI Hub Limit**: 10240MB (10GB) maximum file size
- **Additional Overhead**: Compilation requires extra memory for optimization passes
- **Fundamental Limitation**: Full precision 3B model exceeds platform constraints

---

## 🔬 Experiment 3: FP16 Precision Attempt

### Rationale
Reduce model size by using half-precision (FP16) to fit within QAI Hub's memory constraints.

### Process
```bash
# Convert model to FP16
python convert_precision.py --model orpheus-3b --precision fp16 --output orpheus-fp16.pt

# Attempt QAI Hub deployment
qai-hub-models convert --model orpheus-fp16 --precision fp16 --target-device snapdragon-8-gen-3
```

### Results
❌ **FAILED WITH PIPELINE INCOMPATIBILITY**

### Critical Issue
```
ERROR: QAI Hub compilation pipeline expects FP32 models for input
ERROR: FP16 models not supported in conversion pipeline
ERROR: Quantization requires FP32 source model
```

### Root Cause Analysis
**Catch-22 Situation Identified:**

1. **QAI Hub Requirements**:
   - Expects FP32 models as input for compilation
   - Performs its own quantization during compilation process
   - Does not accept pre-quantized or FP16 models

2. **Memory Constraints**:
   - FP32 3B model: ~12GB (exceeds 10GB limit)
   - FP16 3B model: ~6GB (within limit but not accepted)

3. **Quantization Paradox**:
   - Small models don't need quantization (waste of resources)
   - Large models that would benefit from quantization exceed size limits
   - Platform designed for models in the 1-2B parameter range

---

## 🎯 Conclusions & Lessons Learned

### Technical Limitations Identified

1. **Memory Constraints**
   - QAI Hub's 10GB limit is insufficient for full-precision 3B+ models
   - Platform optimized for smaller, mobile-first model architectures

2. **Pipeline Inflexibility**
   - Rigid FP32-only input requirement prevents workarounds
   - No support for custom precision models or pre-quantized inputs

3. **Architecture Mismatch**
   - Orpheus's specialized audio processing layers require extensive modification
   - Standard conversion pipelines not designed for complex TTS architectures

### Strategic Insights

1. **Model Size vs. Platform Constraints**
   - Current NPU platforms have hard limits that don't align with state-of-the-art model sizes
   - Need to balance model capability with deployment constraints

2. **Quantization Philosophy**
   - QAI Hub's approach assumes quantization is always beneficial
   - Doesn't account for models that are already optimally sized for the platform

3. **Documentation Gaps**
   - Extensive research required to understand input specifications
   - Trial-and-error approach necessary due to incomplete documentation

### Alternative Solutions Implemented

Given the deployment challenges, we pivoted to:

1. **Local Deployment**: Using LM Studio with Orpheus model for development
2. **API Wrapper**: Created FastAPI wrapper around local model for consistent interface
3. **Hybrid Architecture**: Combining local high-quality TTS with cloud-based LLM services

### Future Recommendations

1. **Model Architecture**: Consider developing smaller, NPU-optimized TTS models (1-2B parameters)
2. **Platform Evolution**: Monitor QAI Hub updates for increased memory limits
3. **Edge Deployment**: Explore alternative edge deployment strategies for large models
4. **Quantization Research**: Investigate post-training quantization techniques that maintain audio quality

---

## 📊 Resource Utilization Summary

| Experiment | Model Size | Memory Required | QAI Hub Limit | Status |
|------------|------------|-----------------|---------------|---------|
| Direct ONNX | ~12GB | N/A | 10GB | Failed (Architecture) |
| FP32 Pipeline | ~12GB | ~12.8GB | 10GB | Failed (Memory) |
| FP16 Attempt | ~6GB | ~6.5GB | 10GB | Failed (Pipeline) |

## 🔄 Current Deployment Strategy

**Fallback Solution**: Local deployment with API abstraction
- **Pros**: Full model capability, no size constraints, consistent API
- **Cons**: Requires local GPU/CPU resources, not edge-optimized
- **Performance**: Acceptable for development and demonstration purposes

This experimentation phase provided valuable insights into the current limitations of edge AI deployment platforms and informed our architectural decisions for the final system implementation.