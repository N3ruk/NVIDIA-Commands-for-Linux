import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from unittest.mock import patch
from nvidia_commands.qt import QApplication
from nvidia_commands.core import Hardware
from nvidia_commands.ui import MainWindow, pick

K_COMMAND = ('PROTON_ENABLE_NGX_UPDATER=1 DXVK_NVAPI_DRS_SETTINGS='
             'NGX_DLSS_SR_OVERRIDE=on,NGX_DLSS_SR_OVERRIDE_RENDER_PRESET_SELECTION=render_preset_k %command%')


class TechnologyInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow(Hardware('NVIDIA GeForce RTX 5070', 'rtx50', '595.99', '', [], True, True))
        self.window.show()
        self.app.processEvents()
        self.controls = self.window.feature_controls()

    def tearDown(self):
        self.window.close()
        self.app.processEvents()

    def test_removed_general_panel_and_generic_controls(self):
        self.assertFalse(hasattr(self.window, 'linux_panel'))
        self.assertFalse(hasattr(self.window, 'updater'))
        self.assertNotIn('Ajustes NVIDIA / Linux', [self.window.tabs.tabText(i) for i in range(self.window.tabs.count())])
        self.assertEqual(set(self.controls), {'smooth', 'smooth_queue', 'reflex', 'sharpen', 'sharpen_value', 'film_grain'})
        self.assertEqual(self.window.command.toPlainText(), '')
        self.assertEqual(self.window.result.environment, {})

    def test_exact_k_command_after_reset_and_clipboard(self):
        self.window.reset_button.click()
        pick(self.window.panels['sr'].models, 'K')
        self.window.copy_command()
        self.assertEqual(self.app.clipboard().text(), K_COMMAND)
        self.assertEqual(self.window.command.toPlainText(), K_COMMAND)

    def test_only_updater_has_no_model_or_quality_override(self):
        self.window.update_only.setChecked(True)
        self.assertEqual(self.window.command.toPlainText(), 'PROTON_ENABLE_NGX_UPDATER=1 %command%')
        self.window.update_only.setChecked(False)
        self.assertEqual(self.window.command.toPlainText(), '')
        pick(self.window.panels['sr'].models, 'K')
        self.assertEqual(self.window.command.toPlainText(), K_COMMAND)

    def test_only_smooth_does_not_add_dlss(self):
        pick(self.controls['smooth'], 'on')
        self.window.copy_command()
        self.assertEqual(self.app.clipboard().text(), 'NVPRESENT_ENABLE_SMOOTH_MOTION=1 %command%')
        self.assertEqual(self.window.game_arguments.toPlainText(), '')
        self.assertFalse(self.window.copy_arguments_button.isEnabled())

    def test_smooth_copy_and_fg_conflict(self):
        pick(self.controls['smooth'], 'on')
        pick(self.window.panels['fg'].fg_mode, 'on')
        self.assertFalse(self.window.copy_button.isEnabled())
        self.assertEqual(self.window.command.toPlainText(), '')
        pick(self.window.panels['fg'].fg_mode, 'off')
        self.assertTrue(self.window.copy_button.isEnabled())

    def test_driver_layer_and_gpu_gate_with_recovery(self):
        for driver, layer in [('570.1', True), ('595.99', False)]:
            self.window.hw = Hardware('GeForce RTX 5070', 'rtx50', driver, '', [], layer, True)
            self.window.refresh()
            w = self.controls['smooth']
            self.assertFalse(w.model().item(w.findData('on')).isEnabled())
        self.window.hw = Hardware('GeForce RTX 5070', 'rtx50', '595.99', '', [], True, True)
        pick(self.controls['smooth'], 'on')
        with patch('nvidia_commands.ui.detect_hardware', return_value=Hardware('GeForce RTX 2060', 'rtx20', '595.99')):
            self.window.redetect_hardware()
        self.assertFalse(self.window.copy_button.isEnabled())
        self.assertTrue(self.window.tabs.isTabVisible(self.window.feature_tabs['smooth']))
        pick(self.controls['smooth'], 'game')
        self.assertEqual(self.window.result.errors, [])
        self.assertFalse(self.window.tabs.isTabVisible(self.window.feature_tabs['smooth']))

    def test_native_resets_proton_selections_and_disables_update_only(self):
        pick(self.window.panels['sr'].models, 'K')
        self.window.update_only.setChecked(True)
        pick(self.window.api, 'native_vulkan')
        self.assertEqual(self.window.panels['sr'].models.currentData(), 'game')
        self.assertFalse(self.window.update_only.isChecked())
        self.assertFalse(self.window.update_only.isEnabled())
        self.assertEqual(self.window.command.toPlainText(), '')
        pick(self.window.indicator, 'on')
        self.assertEqual(self.window.command.toPlainText(), '__NGX_SHOW_INDICATOR=1024 %command%')

    def test_reflex_is_only_a_windows_vulkan_bridge(self):
        self.assertFalse(self.window.tabs.isTabVisible(self.window.feature_tabs['reflex']))
        pick(self.window.api, 'vulkan')
        self.controls['reflex'].setChecked(True)
        self.assertEqual(self.window.command.toPlainText(), 'DXVK_NVAPI_VKREFLEX=1 %command%')
        pick(self.window.api, 'dx12')
        self.assertFalse(self.window.copy_button.isEnabled())
        self.controls['reflex'].setChecked(False)
        self.assertEqual(self.window.result.errors, [])

    def test_only_sharpen_has_no_dlss_or_extra_graphics_settings(self):
        pick(self.controls['sharpen'], 'on')
        self.controls['sharpen_value'].setValue(65)
        self.assertEqual(self.window.result.environment, {
            '__GL_SHARPEN_ENABLE': '1', '__GL_SHARPEN_VALUE': '65', '__GL_SHARPEN_IGNORE_FILM_GRAIN': '17'})
        self.assertIn('65 sobre 100', self.window.explanation.toPlainText())

    def test_parallel_outputs_and_separate_clipboards(self):
        pick(self.window.panels['sr'].models, 'K')
        self.window.existing.setPlainText('MANGOHUD=1 %command% -dx12 -fullscreen')
        self.window.copy_command()
        steam = self.app.clipboard().text()
        self.assertIn('DXVK_NVAPI_DRS_SETTINGS', steam)
        self.window.copy_arguments_button.click()
        self.assertEqual(self.app.clipboard().text(), '-dx12 -fullscreen')
        self.assertEqual(self.window.command.toPlainText(), steam)
        self.assertIn('no se aplican', self.window.epic_guide.text())

    def test_epic_rejects_wrappers_without_breaking_steam(self):
        self.window.existing.setPlainText('gamescope -f -- %command% -dx12')
        self.assertTrue(self.window.copy_button.isEnabled())
        self.assertFalse(self.window.copy_arguments_button.isEnabled())
        self.assertIn('wrappers', self.window.epic_guide.text())

    def test_reset_clears_selections_diagnostics_and_conflicts(self):
        original_hw = self.window.hw
        self.window.advanced.setChecked(True)
        self.window.show_unsupported.setChecked(True)
        self.window.options_toggle.setChecked(True)
        self.window.update_only.setChecked(True)
        self.window.existing.setPlainText('UNKNOWN=1 %command% -dx12')
        pick(self.window.panels['sr'].models, 'M')
        pick(self.window.panels['sr'].mode, 'custom')
        self.window.panels['sr'].custom_scale.setValue(50)
        pick(self.window.panels['rr'].models, 'F')
        pick(self.window.panels['fg'].fg_mode, 'dynamic')
        pick(self.window.panels['fg'].multiplier, 6)
        pick(self.controls['smooth'], 'on')
        pick(self.controls['sharpen'], 'on')
        pick(self.window.indicator, 'on')
        self.assertFalse(self.window.copy_button.isEnabled())
        self.window.reset_button.click()
        self.assertIs(self.window.hw, original_hw)
        self.assertEqual(self.window.result.environment, {})
        self.assertEqual(self.window.result.errors, [])
        self.assertEqual(self.window.command.toPlainText(), '')
        self.assertEqual(self.window.game_arguments.toPlainText(), '')
        self.assertEqual(self.window.existing.toPlainText(), '')
        self.assertFalse(self.window.advanced_card.isVisible())
        self.assertFalse(self.window.update_only.isChecked())
        self.assertEqual(self.window.indicator.currentData(), 'game')
        for panel in self.window.panels.values():
            self.assertEqual(panel.models.currentData(), 'game')
        pick(self.controls['smooth'], 'on')
        self.assertEqual(self.window.command.toPlainText(), 'NVPRESENT_ENABLE_SMOOTH_MOTION=1 %command%')

    def test_reset_native_or_invalid_input_is_empty_and_repeatable(self):
        pick(self.window.api, 'opengl')
        pick(self.controls['sharpen'], 'on')
        self.window.existing.setPlainText('%command% %command%')
        self.window.reset_button.click()
        self.window.reset_button.click()
        self.assertEqual(self.window.api.currentData(), 'dxvk')
        self.assertEqual(self.window.result.environment, {})
        self.assertEqual(self.window.result.errors, [])

    def test_selected_values_are_explained(self):
        pick(self.window.panels['sr'].models, 'K')
        pick(self.controls['sharpen'], 'on')
        self.controls['sharpen_value'].setValue(65)
        pick(self.window.panels['fg'].fg_mode, 'dynamic')
        pick(self.window.panels['fg'].multiplier, 4)
        self.window.panels['fg'].target.setValue(200)
        for text in ('65 sobre 100', '3 fotograma(s)', '4×', '200 FPS', 'Super Resolution', 'modelo'):
            self.assertIn(text, self.window.explanation.toPlainText())
