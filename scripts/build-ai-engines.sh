#!/usr/bin/env bash
# Runs inside the target rootfs, with source archives already hash-verified.
set -Eeuo pipefail
cd /opt/agrirobot
mkdir -p bin sources/llama sources/whisper licenses
tar -xzf sources/llama.cpp.tar.gz --strip-components=1 -C sources/llama
tar -xzf sources/whisper.cpp.tar.gz --strip-components=1 -C sources/whisper
for engine in llama whisper; do
    cmake -S "sources/$engine" -B "/tmp/build-$engine" \
      -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DGGML_NATIVE=OFF \
      -DGGML_CUDA=OFF -DGGML_VULKAN=OFF -DGGML_BACKEND_DL=OFF \
      -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF -DWHISPER_BUILD_TESTS=OFF
    if [ "$engine" = llama ]; then
        cmake --build /tmp/build-llama --target llama-server llama-cli -j2
        cp /tmp/build-llama/bin/llama-server /tmp/build-llama/bin/llama-cli bin/
    else
        cmake --build /tmp/build-whisper --target whisper-cli -j2
        cp /tmp/build-whisper/bin/whisper-cli bin/
        cp sources/whisper/samples/jfk.wav data/inference-sample-jfk.wav
    fi
    cp "sources/$engine/LICENSE" "licenses/$engine-MIT.txt"
    rm -rf "/tmp/build-$engine" "sources/$engine"
done
chmod 755 bin/*
