import json
import os
import subprocess
from pathlib import Path
import shlex
import tempfile
import unittest
from unittest.mock import patch
from dlss_studio.core import (CATALOG, Config, Selection, ProfileStore, compatible,
                              family_for, generate, preset, detect_protons, detect_hardware)

class CommandTests(unittest.TestCase):
    def test_rtx2060_k(self):
        result = generate(Config())
        self.assertFalse(result.errors)
        self.assertEqual(result.command.count("%command%"), 1)
        self.assertEqual(result.settings["NGX_DLSS_SR_OVERRIDE_RENDER_PRESET_SELECTION"], "render_preset_k")
        self.assertIn("PROTON_ENABLE_NGX_UPDATER=1", result.command)
        self.assertNotIn("NGX_DLSSG_", result.command)

    def test_game_does_not_request_override_or_updater(self):
        result = generate(Config(sr=Selection()))
        self.assertEqual(result.command, "%command%")

    def test_mode_does_not_require_preset_letter(self):
        result = generate(Config(sr=Selection("game", "quality")))
        self.assertEqual(result.settings["NGX_DLSS_SR_MODE"], "quality")
        self.assertNotIn("NGX_DLSS_SR_OVERRIDE_RENDER_PRESET_SELECTION", result.settings)

    def test_sr_rr_independent(self):
        result = generate(Config(sr=Selection("M", "performance"), rr=Selection("D", "quality")))
        self.assertFalse(result.errors)
        self.assertEqual(result.settings["NGX_DLSS_RR_OVERRIDE_RENDER_PRESET_SELECTION"], "render_preset_d")
        self.assertEqual(result.settings["NGX_DLSS_SR_MODE"], "performance")
        self.assertTrue(any("modos distintos" in w for w in result.warnings))

    def test_cost_warning_for_l_m_only_old_cards(self):
        for letter in ("L", "M"):
            self.assertTrue(any("FP8" in w for w in generate(Config(sr=Selection(letter))).warnings))
            self.assertFalse(any("FP8" in w for w in generate(Config(gpu="rtx50", sr=Selection(letter))).warnings))

    def test_unavailable_or_reserved_presets_never_generate(self):
        for tech in ("sr", "rr", "fg"):
            for model in CATALOG["technologies"][tech]["presets"]:
                if not model["generatable"]:
                    cfg = Config(gpu="rtx50")
                    setattr(cfg, tech, Selection(model["id"]))
                    with self.subTest(tech=tech, preset=model["id"]):
                        result = generate(cfg)
                        self.assertTrue(result.errors)
                        self.assertEqual(result.command, "")

    def test_fg_never_generates_for_20_or_30(self):
        for gpu in ("rtx20", "rtx30", "unknown", "other"):
            result = generate(Config(gpu=gpu, fg=Selection("latest"), fg_mode="on"))
            self.assertTrue(result.errors)
            self.assertFalse(result.command)

    def test_fg_count_is_generated_frames_not_multiplier(self):
        for multiplier in range(2, 7):
            result = generate(Config(gpu="rtx50", fg=Selection("latest"), fg_mode="on", multiplier=multiplier))
            self.assertFalse(result.errors)
            self.assertEqual(result.settings["NGX_DLSSG_MULTI_FRAME_COUNT"], str(multiplier - 1))

    def test_multi_frame_and_dynamic_require_50(self):
        self.assertTrue(generate(Config(gpu="rtx40", fg_mode="on", multiplier=3)).errors)
        self.assertTrue(generate(Config(gpu="rtx40", fg_mode="dynamic")).errors)
        self.assertFalse(generate(Config(gpu="rtx40", fg_mode="on", multiplier=2)).errors)

    def test_dynamic_count_and_target(self):
        result = generate(Config(gpu="rtx50", fg_mode="dynamic", multiplier=6, target_fps=240))
        self.assertFalse(result.errors)
        self.assertEqual(result.settings["NGX_DLSSG_DYNAMIC_MULTI_FRAME_COUNT_MAX"], "5")
        self.assertEqual(result.settings["NGX_DLSSG_DYNAMIC_TARGET_FRAME_RATE"], "240")
        self.assertNotIn("NGX_DLSSG_MULTI_FRAME_COUNT", result.settings)

    def test_bounds_and_unknown_inputs(self):
        for cfg in (Config(sr=Selection("NOT_A_PRESET")), Config(sr=Selection("K", "invalid")),
                    Config(gpu="rtx50", fg_mode="dynamic", target_fps=0),
                    Config(gpu="rtx50", fg_mode="on", multiplier=7)):
            self.assertTrue(generate(cfg).errors)

    def test_keep_wrappers_arguments_and_quoted_values(self):
        cfg = Config(existing='MANGOHUD=1 FOO="a b" gamescope -W 1920 -H 1080 -- %command% -dx12')
        result = generate(cfg)
        self.assertFalse(result.errors)
        tokens = shlex.split(result.command)
        self.assertIn("FOO=a b", tokens)
        self.assertIn("MANGOHUD=1", tokens)
        self.assertEqual(tokens[-8:], ["gamescope", "-W", "1920", "-H", "1080", "--", "%command%", "-dx12"])
        self.assertEqual(result.command.count("%command%"), 1)

    def test_merge_unrelated_drs_and_replace_selected(self):
        cfg = Config(existing='DXVK_NVAPI_DRS_SETTINGS="OTHER_SETTING=7,NGX_DLSS_SR_OVERRIDE_RENDER_PRESET_SELECTION=render_preset_m" '
                    'DXVK_NVAPI_DRS_NGX_DLSS_SR_OVERRIDE_RENDER_PRESET_SELECTION=render_preset_l %command%')
        result = generate(cfg)
        self.assertFalse(result.errors)
        tokens = shlex.split(result.command)
        env = dict(t.split("=", 1) for t in tokens[:-1])
        self.assertIn("OTHER_SETTING=7", env["DXVK_NVAPI_DRS_SETTINGS"])
        self.assertNotIn("DXVK_NVAPI_DRS_NGX_DLSS_SR_OVERRIDE_RENDER_PRESET_SELECTION", env)
        self.assertNotIn("render_preset_l", result.command)
        self.assertNotIn("render_preset_m", result.command)
        self.assertTrue(any("sustituye" in w for w in result.warnings))

    def test_env_prefix_and_append_placeholder(self):
        result = generate(Config(existing="env MANGOHUD=1 mangohud"))
        self.assertFalse(result.errors)
        self.assertTrue(result.command.endswith("mangohud %command%"))
        self.assertIn("MANGOHUD=1", result.command)

    def test_reject_ambiguous_or_complex_inputs_without_executing(self):
        for value in ('%command% %command%', 'foo%command%', 'FOO="unterminated',
                      'echo hello && %command%', '$(touch /tmp/never-do-this) %command%',
                      '%command% > /tmp/example', '%command%\necho x',
                      'mangohud env DXVK_NVAPI_DRS_NGX_DLSS_SR_OVERRIDE=off %command%',
                      'DXVK_NVAPI_DRS_SETTINGS=broken %command%'):
            with self.subTest(value=value):
                result = generate(Config(existing=value))
                self.assertTrue(result.errors)
                self.assertFalse(result.command)

    def test_old_overrides_not_silently_removed(self):
        result = generate(Config(sr=Selection(), existing="DXVK_NVAPI_DRS_NGX_DLSS_FG_OVERRIDE=on %command%"))
        self.assertIn("NGX_DLSS_FG_OVERRIDE=on", result.command)
        self.assertTrue(any("no controlados" in w for w in result.warnings))

    def test_updater_disabled_does_not_delete_existing_options(self):
        result = generate(Config(updater=False, existing="PROTON_ENABLE_NGX_UPDATER=1 %command%"))
        self.assertIn("PROTON_ENABLE_NGX_UPDATER=1", result.command)
        plain = generate(Config(updater=False))
        self.assertNotIn("PROTON_ENABLE_NGX_UPDATER", plain.command)

    def test_detect_proton_does_not_offer_anticheat_runtimes(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            common = home / ".local/share/Steam/steamapps/common"
            proton = common / "Proton - Experimental"
            proton.mkdir(parents=True)
            (proton / "proton").touch()
            (common / "Proton BattlEye Runtime").mkdir()
            (common / "Proton EasyAntiCheat Runtime").mkdir()
            custom = home / ".local/share/Steam/compatibilitytools.d/GE-Proton"
            custom.mkdir(parents=True)
            (custom / "compatibilitytool.vdf").touch()
            with patch("dlss_studio.core.Path.home", return_value=home):
                self.assertEqual(detect_protons(), ["GE-Proton", "Proton - Experimental"])

    def test_frozen_detection_uses_system_library_path(self):
        reply = subprocess.CompletedProcess([], 0, "NVIDIA GeForce RTX 2060, 595.99, 6144 MiB\n", "")
        for original in (None, "/system/custom-libs"):
            with self.subTest(original=original):
                env = {"LD_LIBRARY_PATH": "/bundled/qt"}
                if original is not None:
                    env["LD_LIBRARY_PATH_ORIG"] = original
                with patch.dict(os.environ, env, clear=True), \
                     patch("dlss_studio.core.sys.frozen", True, create=True), \
                     patch("dlss_studio.core.subprocess.run", return_value=reply) as run:
                    self.assertEqual(detect_hardware().family, "rtx20")
                    self.assertEqual(run.call_args.kwargs["env"].get("LD_LIBRARY_PATH"), original)
                    self.assertEqual(os.environ["LD_LIBRARY_PATH"], "/bundled/qt")

    def test_hardware_families(self):
        self.assertEqual(family_for("NVIDIA GeForce RTX 2060"), "rtx20")
        self.assertEqual(family_for("NVIDIA GeForce RTX 4070 Ti"), "rtx40")
        self.assertEqual(family_for("NVIDIA GeForce RTX 5090 Laptop GPU"), "rtx50")
        self.assertEqual(family_for("AMD Radeon RX 6800"), "unknown")
        self.assertFalse(compatible("fg", "rtx20"))

    def test_catalog_sources_and_rr_not_sr(self):
        self.assertEqual(preset("sr", "M")["generation"], "DLSS 4.5 · Super Resolution")
        self.assertFalse(preset("rr", "M")["generatable"])
        for tech in CATALOG["technologies"].values():
            ids = [p["id"] for p in tech["presets"]]
            self.assertEqual(len(ids), len(set(ids)))
            for model in tech["presets"]:
                for source in model["sources"]:
                    self.assertTrue(CATALOG["sources"][source]["url"].startswith("https://"))

class ProfileTests(unittest.TestCase):
    def test_roundtrip_unicode_and_private_permissions(self):
        with tempfile.TemporaryDirectory() as temp:
            store = ProfileStore(Path(temp) / "nested/profiles.json")
            self.assertEqual(store.load(), {})
            state = {"config": {"existing": "MANGOHUD=1 %command%"}, "name": "Prueba"}
            store.save("Cyberpunk · comparación", state)
            store.save("Otro", {"example": True})
            self.assertEqual(store.load()["Cyberpunk · comparación"], state)
            self.assertEqual(store.path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(len(store.load()), 2)

    def test_corrupted_profile_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "profiles.json"
            p.write_text("not valid json")
            store = ProfileStore(p)
            with self.assertRaises(ValueError):
                store.save("x", {})
            self.assertEqual(p.read_text(), "not valid json")

if __name__ == "__main__":
    unittest.main()
