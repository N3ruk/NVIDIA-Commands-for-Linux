"""Behavioral regressions for explicit feature scope and required updates."""
import unittest
from nvidia_commands.core import CATALOG, Config, Selection, generate


class CommandScopeTests(unittest.TestCase):
    def test_clean_start_has_no_implicit_technology(self):
        result = generate(Config())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.environment, {})
        self.assertEqual(result.command, '%command%')

    def test_exact_k_command_on_supported_proton_apis_and_gpus(self):
        expected = ('PROTON_ENABLE_NGX_UPDATER=1 DXVK_NVAPI_DRS_SETTINGS='
                    'NGX_DLSS_SR_OVERRIDE=on,NGX_DLSS_SR_OVERRIDE_RENDER_PRESET_SELECTION=render_preset_k %command%')
        for api in ('dxvk', 'dx12', 'vulkan'):
            for gpu in ('rtx20', 'rtx30', 'rtx40', 'rtx50'):
                with self.subTest(api=api, gpu=gpu):
                    self.assertEqual(generate(Config(api=api, gpu=gpu, sr=Selection('K'))).command, expected)

    def test_each_preset_only_requests_its_own_technology(self):
        for tech in ('sr', 'rr', 'fg'):
            for model in CATALOG['technologies'][tech]['presets']:
                if not model['generatable'] or model['id'] == 'game':
                    continue
                with self.subTest(technology=tech, model=model['id']):
                    cfg = Config(gpu='rtx50')
                    setattr(cfg, tech, Selection(model['id']))
                    r = generate(cfg)
                    self.assertEqual(r.errors, [])
                    self.assertEqual(set(r.environment), {'PROTON_ENABLE_NGX_UPDATER', 'DXVK_NVAPI_DRS_SETTINGS'})
                    stem = 'NGX_DLSS_' + tech.upper()
                    self.assertEqual(r.settings, {stem + '_OVERRIDE': 'on',
                        stem + '_OVERRIDE_RENDER_PRESET_SELECTION': 'render_preset_' + model['id'].lower()})

    def test_quality_only_does_not_select_a_model_or_other_technology(self):
        r = generate(Config(sr=Selection('game', 'quality')))
        self.assertEqual(r.settings, {'NGX_DLSS_SR_OVERRIDE': 'on', 'NGX_DLSS_SR_MODE': 'quality'})
        self.assertEqual(r.environment['PROTON_ENABLE_NGX_UPDATER'], '1')

    def test_update_only_does_not_override_models(self):
        r = generate(Config(update_only=True))
        self.assertEqual(r.command, 'PROTON_ENABLE_NGX_UPDATER=1 %command%')
        self.assertEqual(r.settings, {})
        for api in ('opengl', 'native_vulkan'):
            self.assertTrue(generate(Config(update_only=True, api=api)).errors)
        self.assertTrue(generate(Config(update_only=True, gpu='unknown')).errors)

    def test_disabling_fg_does_not_update_or_touch_sr_rr(self):
        r = generate(Config(gpu='rtx50', fg_mode='off'))
        self.assertEqual(r.errors, [])
        self.assertEqual(r.settings, {'NGX_DLSS_FG_OVERRIDE': 'on', 'NGX_DLSSG_MODE': 'off'})
        self.assertNotIn('PROTON_ENABLE_NGX_UPDATER', r.environment)

    def test_smooth_only_and_opt_in_overlay_workaround(self):
        c = Config(gpu='rtx50', driver='595.99', smooth='on', smooth_layer=True)
        self.assertEqual(generate(c).command, 'NVPRESENT_ENABLE_SMOOTH_MOTION=1 %command%')
        c.smooth_queue = True
        self.assertEqual(generate(c).environment, {'NVPRESENT_ENABLE_SMOOTH_MOTION': '1', 'NVPRESENT_QUEUE_FAMILY': '1'})

    def test_numeric_fg_override_and_named_numeric_modes_conflict(self):
        for setting in ('NGX_DLSS_FG_OVERRIDE=1', 'NGX_DLSS_FG_OVERRIDE=0X1',
                        'NGX_DLSSG_MODE=2', 'NGX_DLSSG_MODE=0x3', 'NGX_DLSSG_MODE=dynamic'):
            c = Config(gpu='rtx50', smooth='on', smooth_layer=True,
                       existing='DXVK_NVAPI_DRS_SETTINGS=' + setting + ' %command%')
            self.assertTrue(generate(c).errors, setting)
            self.assertEqual(generate(c).command, '')

    def test_imported_explicit_fg_off_is_compatible_with_smooth(self):
        c = Config(gpu='rtx50', smooth='on', smooth_layer=True,
                   existing='DXVK_NVAPI_DRS_SETTINGS=NGX_DLSS_FG_OVERRIDE=1,NGX_DLSSG_MODE=0x1 %command%')
        self.assertEqual(generate(c).errors, [])

    def test_smooth_rejects_applying_layer_to_gamescope(self):
        for wrapper in ('gamescope', '/usr/bin/gamescope'):
            c = Config(gpu='rtx50', smooth='on', smooth_layer=True, existing=wrapper + ' -f -- %command%')
            self.assertTrue(generate(c).errors)
            self.assertEqual(generate(c).command, '')

    def test_reflex_cannot_be_enabled_while_import_disables_layer(self):
        c = Config(api='vulkan', reflex=True, reflex_layer=True,
                   existing='DISABLE_DXVK_NVAPI_VKREFLEX=1 %command%')
        self.assertTrue(generate(c).errors)
        self.assertEqual(generate(c).command, '')

    def test_presets_override_disabled_updater_but_preserve_explicit_user_args(self):
        c = Config(sr=Selection('K'), existing='PROTON_ENABLE_NGX_UPDATER=0 USER_OPTION=1 %command% -dx12')
        r = generate(c)
        self.assertEqual(r.errors, [])
        self.assertEqual(r.environment['PROTON_ENABLE_NGX_UPDATER'], '1')
        self.assertEqual(r.environment['USER_OPTION'], '1')
        self.assertTrue(r.command.endswith('%command% -dx12'))

    def test_imported_model_requests_receive_their_update_dependency(self):
        r = generate(Config(existing='DXVK_NVAPI_DRS_SETTINGS=NGX_DLSS_SR_OVERRIDE=on,NGX_DLSS_SR_OVERRIDE_RENDER_PRESET_SELECTION=render_preset_k %command%'))
        self.assertEqual(r.errors, [])
        self.assertEqual(r.environment['PROTON_ENABLE_NGX_UPDATER'], '1')
        self.assertNotIn('NGX_DLSS_RR', r.command)
        self.assertNotIn('NGX_DLSS_FG', r.command)
