import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from unittest.mock import patch
from nvidia_commands.qt import QApplication
from nvidia_commands.ui import MainWindow, pick
from nvidia_commands.core import Hardware

class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.dialogs = patch("nvidia_commands.ui.QMessageBox.warning", side_effect=AssertionError("Diálogo inesperado"))
        self.dialogs.start()
        self.window = MainWindow(Hardware("NVIDIA GeForce RTX 2060", "rtx20", "595.99.02", "6144 MiB"))
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.dialogs.stop()
        self.window.close()
        self.app.processEvents()

    def detect(self, family, name):
        with patch("nvidia_commands.ui.detect_hardware", return_value=Hardware(name, family, "595.99.02")):
            self.window.redetect_hardware()

    def test_initial_real_gpu_and_command(self):
        self.assertEqual(self.window.config().gpu, "rtx20")
        self.assertIn("RTX 2060", self.window.hardware_label.text())
        self.assertIn("render_preset_k", self.window.command.toPlainText())
        self.assertNotIn("NGX_DLSS_RR_OVERRIDE", self.window.command.toPlainText())
        self.assertFalse(self.window.tabs.isTabVisible(2))
        self.assertTrue(self.window.copy_button.isEnabled())

    def test_only_configurator_no_context_form(self):
        self.assertEqual(self.window.stack.count(), 1)
        for removed in ("gpu", "proton", "resolution", "goal", "integration", "nav"):
            self.assertFalse(hasattr(self.window, removed), removed)
        self.assertFalse(self.window.advanced_card.isVisible())
        self.window.options_toggle.click()
        self.assertTrue(self.window.advanced_card.isVisible())

    def test_generation_visible_for_each_modern_sr_preset(self):
        sr = self.window.panels["sr"]
        for key, generation in (("K", "4.0"), ("J", "4.0"), ("L", "4.5"), ("M", "4.5")):
            pick(sr.models, key)
            self.assertEqual(sr.models.currentText(), f"{key} · DLSS {generation}")
            self.assertEqual(sr.generation.text(), f"DLSS {generation}")
            self.assertIn(f"DLSS {generation}", sr.description.toPlainText())
            self.assertIn(f"render_preset_{key.lower()}", self.window.command.toPlainText())

    def test_unfixed_and_historical_generations_are_honest(self):
        sr = self.window.panels["sr"]
        pick(sr.models, "game")
        self.assertIn("sin fijar", sr.generation.text())
        pick(sr.models, "latest")
        self.assertIn("variable", sr.generation.text())
        self.window.advanced.setChecked(True)
        pick(sr.models, "E")
        self.assertIn("2.x / 3.x", sr.generation.text())
        self.assertIn("no fija una versión exacta", sr.description.toPlainText())

    def test_rr_generation_not_confused_with_sr_letters(self):
        rr = self.window.panels["rr"]
        for key in ("D", "E", "F"):
            pick(rr.models, key)
            self.assertIn("DLSS 4+", rr.generation.text())
            self.assertIn("versión exacta", rr.description.toPlainText())
        self.assertEqual(self.window.panels["sr"].models.currentData(), "K")

    def test_change_preset_mode_and_copy(self):
        pick(self.window.panels["sr"].models, "M")
        pick(self.window.panels["sr"].mode, "performance")
        self.window.copy_button.click()
        text = self.app.clipboard().text()
        self.assertIn("render_preset_m", text)
        self.assertIn("NGX_DLSS_SR_MODE=performance", text)
        self.assertEqual(text.count("%command%"), 1)

    def test_gpu_does_not_change_sr_command_syntax(self):
        command = self.window.command.toPlainText()
        self.detect("rtx50", "NVIDIA GeForce RTX 5090")
        self.assertEqual(command, self.window.command.toPlainText())
        self.assertTrue(self.window.tabs.isTabVisible(2))
        self.assertIn("RTX 5090", self.window.hardware_label.text())

    def test_future_gpu_and_dynamic_six_x(self):
        self.detect("rtx50", "NVIDIA GeForce RTX 5090")
        fg = self.window.panels["fg"]
        pick(fg.models, "latest")
        pick(fg.fg_mode, "dynamic")
        pick(fg.multiplier, 6)
        fg.target.setValue(240)
        self.assertIn("NGX_DLSSG_DYNAMIC_MULTI_FRAME_COUNT_MAX=5", self.window.command.toPlainText())
        self.assertIn("DLSS 4.5", fg.generation.text())
        self.assertTrue(self.window.copy_button.isEnabled())

    def test_rtx40_disallows_mfg_and_dynamic_but_supports_fg(self):
        self.detect("rtx40", "NVIDIA GeForce RTX 4070")
        fg = self.window.panels["fg"]
        self.assertFalse(fg.fg_mode.model().item(fg.fg_mode.findData("dynamic")).isEnabled())
        self.assertFalse(fg.multiplier.model().item(fg.multiplier.findData(3)).isEnabled())
        pick(fg.fg_mode, "on")
        self.assertIn("NGX_DLSSG_MULTI_FRAME_COUNT=1", self.window.command.toPlainText())
        self.assertIn("DLSS 3+", fg.generation.text())

    def test_unsupported_fg_is_browsable_without_activating_it(self):
        self.window.show_unsupported.setChecked(True)
        self.assertTrue(self.window.tabs.isTabVisible(2))
        fg = self.window.panels["fg"]
        self.assertFalse(fg.fg_mode.model().item(fg.fg_mode.findData("on")).isEnabled())
        self.assertIn("No compatible", fg.availability.text())
        self.assertTrue(self.window.copy_button.isEnabled())

    def test_switching_to_incompatible_hardware_can_recover(self):
        self.detect("rtx50", "NVIDIA GeForce RTX 5090")
        pick(self.window.panels["fg"].fg_mode, "dynamic")
        self.detect("rtx20", "NVIDIA GeForce RTX 2060")
        self.assertFalse(self.window.copy_button.isEnabled())
        self.assertTrue(self.window.tabs.isTabVisible(2))
        pick(self.window.panels["fg"].fg_mode, "game")
        self.assertTrue(self.window.copy_button.isEnabled())

    def test_unknown_gpu_detection_can_recover(self):
        self.detect("unknown", "GPU no identificada")
        self.assertFalse(self.window.copy_button.isEnabled())
        self.assertTrue(self.window.retry_detection.isVisible())
        self.detect("rtx20", "NVIDIA GeForce RTX 2060")
        self.assertTrue(self.window.copy_button.isEnabled())
        self.assertFalse(self.window.retry_detection.isVisible())

    def test_reserved_prevents_copy(self):
        self.window.advanced.setChecked(True)
        pick(self.window.panels["sr"].models, "H")
        self.assertFalse(self.window.copy_button.isEnabled())
        self.assertEqual(self.window.command.toPlainText(), "")
        self.assertIn("Reservado", self.window.notice.toPlainText())

    def test_bad_command_error_then_recover(self):
        self.window.existing.setPlainText("%command% %command%")
        self.assertFalse(self.window.copy_button.isEnabled())
        self.window.existing.setPlainText("MANGOHUD=1 gamescope -f -- %command%")
        self.assertTrue(self.window.copy_button.isEnabled())
        self.assertIn("gamescope -f -- %command%", self.window.command.toPlainText())

if __name__ == "__main__":
    unittest.main()
