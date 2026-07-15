# M0-R4 Toolchain Evidence

## Rust/Cargo

Initial state:

```text
cargo --version -> command not found
rustc --version -> command not found
rustup --version -> command not found
brew --version -> Homebrew 5.0.4
```

Actions:

- Attempted `brew install rust`.
- First attempts exposed insufficient disk space while installing LLVM.
- Ran approved Homebrew cleanup and retried after disk space recovered.
- Final `brew install rust` succeeded.

Final state:

```text
cargo 1.97.0 (c980f4866 2026-06-30) (Homebrew)
rustc 1.97.0 (2d8144b78 2026-07-07) (Homebrew)
```

## Node/npm

Issue found:

```text
node 25.9.0_2 failed to load /opt/homebrew/opt/llhttp/lib/libllhttp.9.3.dylib
brew linkage node reported broken dependency: llhttp
```

Action:

- Ran approved `brew reinstall node`.
- Closed Homebrew developer mode after `brew linkage node` enabled it.

Final state:

```text
node v26.5.0
npm 11.17.0
brew linkage node -> no broken dependency reported
```

## Cargo Registry Stability

Issue found:

- `cargo test --workspace` initially failed in sandbox because `index.crates.io` DNS was blocked.
- Escalated cargo access reached crates.io but Tauri dependency download was slow and failed once on `bs58 v0.5.1` with `Broken pipe`.

Action:

- Added `wt-media-desktop/.cargo/config.toml` with sparse registry, lower slow-network threshold, longer timeout, retry count and disabled multiplexing.

Final result:

- `cargo test --workspace`: PASS.
- `npm run build` / `tauri build`: PASS.

## Status

PASS. Toolchain is now usable for M0-R4 Desktop local build and verification.
