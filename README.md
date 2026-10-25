# LineageOS 23.0 build launcher for Redmi Pad (yunluo)

A **device-only GitHub repository** for trying an unofficial LineageOS 23.0 / Android 16 build for Xiaomi Redmi Pad (`yunluo`). This repository **does not contain the Android OS source or vendor binaries**.

## Repositories used

The local manifest is based on the [xiaomi-mt6789-devs](https://github.com/xiaomi-mt6789-devs) LineageOS 23.0 device sources:

- `device/xiaomi/yunluo` — device tree
- `device/xiaomi/yunluo-kernel` — **prebuilt kernel, DTB and modules**, not the full kernel source
- `device/mediatek/sepolicy_vndr` — vendor SELinux
- `hardware/mediatek` — hardware support
- `hardware/xiaomi` — LineageOS Xiaomi hardware
- `vendor/xiaomi/yunluo` — proprietary vendor files

The full LineageOS **base platform source is still required** to compile an actual ROM. The workflow downloads it on the build runner using `repo sync`. Merely syncing device configs cannot produce a ROM.

## Actions

Open [Actions → LineageOS yunluo builder](../../actions/workflows/build-lineage.yml).

**Validate (automatic on push, or manual):** checks local-manifest XML, project paths, upstream repositories and branches. Does **not** download Android sources. This is safe on a standard GitHub-hosted runner.

**Build (manual):** choose `mode = build`; default runner `self-hosted`. Requires a properly registered Linux x86_64 GitHub Actions self-hosted runner with **at least ~300 GB free disk recommended**, **16+ GiB RAM** (more is better), and enough time. The build job rejects <240 GiB free disk early to avoid wasting hours. It does not compile the huge kernel source tree; it uses the checked-in upstream prebuilt kernel repository.

You may select `ubuntu-24.04` instead to test the disk-space gate, but standard GitHub-hosted runners **do not provide enough disk space for full LineageOS builds**. For a full build on GitHub infrastructure, configure a suitable larger runner and update its label in the workflow.

The build uses the normal LineageOS `lineage-23.0` manifest, partial + shallow Git sync, and `lineage_yunluo-userdebug` / `m bacon`. Shallow/partial clones reduce Git history and transfer; they cannot eliminate required Android sources.

## Files

- `local_manifests/yunluo.xml`: device-specific project references
- `scripts/validate_manifest.py`: static and remote validation
- `.github/workflows/build-lineage.yml`: validation and build pipeline

## Outputs

A successful build uploads the `lineage-*.zip` and `SHA256SUMS.txt` as GitHub Actions artifacts. Workflow artifacts expire according to configured retention; these are not permanent GitHub Releases.

## Important

**Experimental, unofficial, untested. No working/booting ROM is promised.** The upstream trees may need additional fixes as LineageOS 23.0 evolves. Do **not** flash a build until boot, vendor, AVB, partition and device compatibility have been checked; keep a stock firmware recovery path. This project does **not** modify the user's already-working nAa kernel repository.
