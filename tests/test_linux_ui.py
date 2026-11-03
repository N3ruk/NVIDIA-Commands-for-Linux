import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from unittest.mock import patch
from nvidia_commands.qt import QApplication
from nvidia_commands.core import Hardware
from nvidia_commands.ui import MainWindow,pick

class LinuxInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.window=MainWindow(Hardware('NVIDIA GeForce RTX 5070','rtx50','595.99','12288 MiB',[],True,True))
        self.window.show();self.app.processEvents()
    def tearDown(self):self.window.close();self.app.processEvents()
    def test_brand_and_gpu(self):
        self.assertIn('NVIDIA Commands for Linux',self.window.windowTitle())
        self.assertTrue(self.window.tabs.isTabVisible(2))
        self.assertEqual(self.window.config().gpu,'rtx50')
    def test_smooth_copy_and_conflict(self):
        pick(self.window.linux_panel.controls['smooth'],'on')
        self.window.copy_command()
        self.assertIn('NVPRESENT_ENABLE_SMOOTH_MOTION=1',self.app.clipboard().text())
        pick(self.window.panels['fg'].fg_mode,'on')
        self.assertFalse(self.window.copy_button.isEnabled())
        pick(self.window.panels['fg'].fg_mode,'off')
        self.assertTrue(self.window.copy_button.isEnabled())
    def test_detecting_rtx20_hides_smooth_but_allows_recovery(self):
        pick(self.window.linux_panel.controls['smooth'],'on')
        with patch('nvidia_commands.ui.detect_hardware',return_value=Hardware('GeForce RTX 2060','rtx20','595.99')):self.window.redetect_hardware()
        self.assertFalse(self.window.copy_button.isEnabled())
        pick(self.window.linux_panel.controls['smooth'],'game')
        self.assertTrue(self.window.copy_button.isEnabled())
        self.assertTrue(self.window.linux_panel.rows['smooth'].isHidden())
    def test_driver_and_layer_control_availability(self):
        for driver,layer in [('570.1',True),('595.99',False)]:
            self.window.hw=Hardware('GeForce RTX 5070','rtx50',driver,'',[],layer,True)
            self.window.refresh()
            w=self.window.linux_panel.controls['smooth']
            self.assertFalse(w.model().item(w.findData('on')).isEnabled())
    def test_api_switch_to_native_drops_proton_presets(self):
        pick(self.window.api,'native_vulkan')
        self.assertEqual(self.window.panels['sr'].models.currentData(),'game')
        self.assertNotIn('DXVK_NVAPI',self.window.command.toPlainText())
        self.assertEqual(self.window.command.toPlainText(), '')
        self.assertFalse(self.window.copy_button.isEnabled())
        pick(self.window.linux_panel.controls['indicator'],'on')
        self.assertIn('__NGX_SHOW_INDICATOR=1024',self.window.command.toPlainText())
    def test_api_restrictions_allow_reset(self):
        pick(self.window.linux_panel.controls['anisotropy'],16)
        pick(self.window.api,'dx12')
        self.assertFalse(self.window.copy_button.isEnabled())
        self.assertFalse(self.window.linux_panel.rows['anisotropy'].isHidden())
        pick(self.window.linux_panel.controls['anisotropy'],-1)
        self.assertTrue(self.window.copy_button.isEnabled())
        self.assertTrue(self.window.linux_panel.rows['anisotropy'].isHidden())
    def test_parallel_outputs_and_separate_clipboards(self):
        self.assertFalse(hasattr(self.window, 'launcher'))
        self.assertFalse(hasattr(self.window, 'epic_path'))
        self.assertTrue(self.window.command.isVisible())
        self.assertTrue(self.window.game_arguments.isVisible())
        self.window.existing.setPlainText('MANGOHUD=1 %command% -dx12 -fullscreen')
        self.window.copy_command()
        steam = self.app.clipboard().text()
        self.assertIn('DXVK_NVAPI_DRS_SETTINGS', steam)
        self.assertIn('%command% -dx12 -fullscreen', steam)
        self.window.copy_arguments_button.click()
        self.assertEqual(self.app.clipboard().text(), '-dx12 -fullscreen')
        self.assertEqual(self.window.command.toPlainText(), steam)
        self.assertIn('no se aplican', self.window.epic_guide.text())

    def test_epic_has_no_false_equivalent_for_variables(self):
        pick(self.window.linux_panel.controls['smooth'], 'on')
        self.assertIn('NVPRESENT_ENABLE_SMOOTH_MOTION=1', self.window.command.toPlainText())
        self.assertEqual(self.window.game_arguments.toPlainText(), '')
        self.assertFalse(self.window.copy_arguments_button.isEnabled())

    def test_epic_rejects_wrappers_without_breaking_steam(self):
        self.window.existing.setPlainText('gamescope -f -- %command% -dx12')
        self.assertTrue(self.window.copy_button.isEnabled())
        self.assertFalse(self.window.copy_arguments_button.isEnabled())
        self.assertIn('wrappers', self.window.epic_guide.text())

    def test_opengl_controls_visible_only_for_opengl(self):
        self.assertTrue(self.window.linux_panel.rows['gl_vrr'].isHidden())
        pick(self.window.api,'opengl')
        self.assertFalse(self.window.linux_panel.rows['gl_vrr'].isHidden())
        pick(self.window.linux_panel.controls['gl_vrr'],'on')
        self.assertIn('__GL_VRR_ALLOWED=1',self.window.command.toPlainText())
    def test_only_graphics_controls_no_generic_wrappers(self):
        for key in ('gamescope', 'scaling_size', 'hud', 'hdr', 'prime'):
            self.assertNotIn(key, self.window.linux_panel.controls)
        for key in ('smooth', 'reflex', 'sharpen', 'fps', 'vsync', 'indicator'):
            self.assertIn(key, self.window.linux_panel.controls)

    def test_reset_clears_all_settings_and_recovers_from_conflict(self):
        original_hw = self.window.hw
        self.window.advanced.setChecked(True)
        self.window.show_unsupported.setChecked(True)
        self.window.options_toggle.setChecked(True)
        self.window.existing.setPlainText('UNKNOWN=1 %command% -dx12')
        pick(self.window.panels['sr'].models, 'M')
        pick(self.window.panels['sr'].mode, 'custom')
        self.window.panels['sr'].custom_scale.setValue(50)
        pick(self.window.panels['rr'].models, 'F')
        pick(self.window.panels['fg'].models, 'latest')
        pick(self.window.panels['fg'].fg_mode, 'dynamic')
        pick(self.window.panels['fg'].multiplier, 6)
        self.window.panels['fg'].target.setValue(240)
        pick(self.window.linux_panel.controls['smooth'], 'on')
        pick(self.window.linux_panel.controls['sharpen'], 'on')
        self.window.linux_panel.controls['sharpen_value'].setValue(90)
        self.window.linux_panel.controls['fps'].setValue(120)
        self.assertFalse(self.window.copy_button.isEnabled())
        self.window.reset_button.click()
        self.assertIs(self.window.hw, original_hw)
        self.assertEqual(self.window.command.toPlainText(), '')
        self.assertEqual(self.window.game_arguments.toPlainText(), '')
        self.assertEqual(self.window.existing.toPlainText(), '')
        self.assertFalse(self.window.copy_button.isEnabled())
        self.assertFalse(self.window.copy_arguments_button.isEnabled())
        self.assertFalse(self.window.updater.isChecked())
        self.assertFalse(self.window.advanced.isChecked())
        self.assertFalse(self.window.show_unsupported.isChecked())
        self.assertFalse(self.window.advanced_card.isVisible())
        self.assertEqual(self.window.result.environment, {})
        self.assertEqual(self.window.config().multiplier, 2)
        self.assertEqual(self.window.config().target_fps, 144)
        self.assertEqual(self.window.config().sr.scale, 67)
        for panel in self.window.panels.values():
            self.assertEqual(panel.models.currentData(), 'game')
        pick(self.window.linux_panel.controls['smooth'], 'on')
        self.assertTrue(self.window.copy_button.isEnabled())
        self.assertNotIn('NGX_DLSS_SR', self.window.command.toPlainText())
        self.assertNotIn('UNKNOWN', self.window.command.toPlainText())

    def test_reset_native_or_invalid_input_is_empty_and_repeatable(self):
        pick(self.window.api, 'opengl')
        pick(self.window.linux_panel.controls['gl_vrr'], 'on')
        self.window.existing.setPlainText('%command% %command%')
        self.window.reset_button.click()
        self.window.reset_button.click()
        self.assertEqual(self.window.api.currentData(), 'dxvk')
        self.assertEqual(self.window.result.environment, {})
        self.assertEqual(self.window.command.toPlainText(), '')
        self.assertEqual(self.window.result.errors, [])

    def test_explanations_describe_effects_and_selected_values(self):
        self.window.linux_panel.controls['fps'].setValue(117)
        pick(self.window.linux_panel.controls['sharpen'], 'on')
        self.window.linux_panel.controls['sharpen_value'].setValue(65)
        pick(self.window.panels['fg'].fg_mode, 'dynamic')
        pick(self.window.panels['fg'].multiplier, 4)
        self.window.panels['fg'].target.setValue(200)
        text = self.window.explanation.toPlainText()
        for explanation in ('117 FPS', '65 sobre 100', '3 fotograma(s)', '4×', '200 FPS', 'DirectX 9', 'Super Resolution', 'modelo'):
            self.assertIn(explanation, text)

    def test_disabled_anisotropy_remains_resettable_on_dx12(self):
        pick(self.window.linux_panel.controls['anisotropy'],0)
        pick(self.window.api,'dx12')
        self.assertFalse(self.window.linux_panel.rows['anisotropy'].isHidden())
        self.assertTrue(self.window.linux_panel.controls['anisotropy'].isEnabled())
        self.assertFalse(self.window.copy_button.isEnabled())
        pick(self.window.linux_panel.controls['anisotropy'],-1)
        self.assertTrue(self.window.copy_button.isEnabled())
