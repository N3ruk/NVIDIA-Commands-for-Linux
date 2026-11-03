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
        self.assertTrue(self.window.copy_button.isEnabled())
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
    def test_epic_path_and_separate_clipboard(self):
        pick(self.window.launcher,'epic')
        self.assertTrue(self.window.epic_card.isVisible())
        self.assertFalse(self.window.copy_button.isEnabled())
        self.window.epic_path.setText('/home/user/Epic Games.AppImage')
        self.window.existing.setPlainText('%command% -dx12')
        self.window.copy_command()
        text=self.app.clipboard().text()
        self.assertNotIn('%command%',text)
        self.assertNotIn('-dx12',text)
        self.assertIn('/home/user/Epic Games.AppImage',text)
        self.assertIn('toda la sesión',self.window.output_guide.text())
        self.window.copy_arguments_button.click()
        self.assertEqual(self.app.clipboard().text(),'-dx12')
    def test_steam_and_epic_switch_retains_existing(self):
        self.window.existing.setPlainText('MANGOHUD=1 %command% -dx12')
        before=self.window.command.toPlainText()
        pick(self.window.launcher,'epic');self.window.epic_path.setText('/opt/epic')
        pick(self.window.launcher,'steam')
        self.assertEqual(self.window.command.toPlainText(),before)
    def test_opengl_controls_visible_only_for_opengl(self):
        self.assertTrue(self.window.linux_panel.rows['gl_vrr'].isHidden())
        pick(self.window.api,'opengl')
        self.assertFalse(self.window.linux_panel.rows['gl_vrr'].isHidden())
        pick(self.window.linux_panel.controls['gl_vrr'],'on')
        self.assertIn('__GL_VRR_ALLOWED=1',self.window.command.toPlainText())
    def test_gamescope_copy(self):
        pick(self.window.linux_panel.controls['gamescope'],'nis')
        self.window.copy_command()
        self.assertIn('gamescope -w 1280 -h 720 -W 1920 -H 1080 -F nis -- %command%',self.app.clipboard().text())
    def test_disabled_anisotropy_remains_resettable_on_dx12(self):
        pick(self.window.linux_panel.controls['anisotropy'],0)
        pick(self.window.api,'dx12')
        self.assertFalse(self.window.linux_panel.rows['anisotropy'].isHidden())
        self.assertTrue(self.window.linux_panel.controls['anisotropy'].isEnabled())
        self.assertFalse(self.window.copy_button.isEnabled())
        pick(self.window.linux_panel.controls['anisotropy'],-1)
        self.assertTrue(self.window.copy_button.isEnabled())
