import unittest
from nvidia_commands.core import Config, Selection, generate, epic_arguments
from nvidia_commands.explanations import explain_result


class ExplanationTests(unittest.TestCase):
    def explanations(self, **changes):
        result = generate(Config(gpu='rtx50', driver='595.99', smooth_layer=True, **changes))
        self.assertEqual(result.errors, [])
        return dict(explain_result(result))

    def test_combined_dxvk_and_drs_are_expanded(self):
        entries = self.explanations(fps=90, vsync='off', anisotropy=16, lod_bias='-0.5', low_latency='on')
        for key in ('dxgi.maxFrameRate=90', 'd3d9.maxFrameRate=90', 'dxgi.syncInterval=0',
                    'd3d11.samplerAnisotropy=16', 'd3d11.samplerLodBias=-0.5', 'dxvk.latencySleep=True'):
            self.assertIn(key, entries)
            self.assertGreater(len(entries[key]), 50)
        self.assertIn('render_preset_k', '\n'.join(entries))
        self.assertIn('DLSS 4.0', '\n'.join(entries.values()))

    def test_every_public_environment_has_a_meaning(self):
        selections = [dict(smooth='on', smooth_queue=True), dict(reflex=True, api='vulkan'),
                      dict(sharpen='on', api_osd=True), dict(indicator='on'),
                      dict(api='native_vulkan', sr=Selection(), indicator='on'),
                      dict(api='dx12', fps=72), dict(api='opengl', sr=Selection(), vsync='on',
                      anisotropy=16, gl_threaded='on', gl_cache='off', gl_fxaa='on', gl_vrr='on')]
        for changes in selections:
            with self.subTest(changes=changes):
                entries = self.explanations(**changes)
                for text in entries.values():
                    self.assertNotIn('no está catalogada', text)
                    self.assertGreater(len(text), 45)

    def test_unknown_imported_values_are_not_invented(self):
        entries = self.explanations(existing="UNKNOWN=1 DXVK_CONFIG='unknown.option=1' DXVK_NVAPI_DRS_SETTINGS='UNKNOWN_DRS=7' %command%")
        self.assertIn('No está catalogada', entries['UNKNOWN=1'])
        self.assertIn('no catalogado', entries['unknown.option=1'])
        self.assertIn('no está catalogado', entries['UNKNOWN_DRS=7'])

    def test_custom_ratio_and_dlaa_have_distinct_meanings(self):
        entries = self.explanations(sr=Selection('M', 'custom', 50), rr=Selection('F', 'dlaa'))
        self.assertIn('50 % de cada dimensión', entries['NGX_DLSS_SR_OVERRIDE_SCALING_RATIO=50'])
        self.assertIn('sin reescalado', entries['NGX_DLSS_RR_MODE=dlaa'])

    def test_persistent_indicators_explain_reset_limit(self):
        entries = self.explanations(indicator='off')
        self.assertIn('Reset solo limpia el generador', entries['DXVK_NVAPI_SET_NGX_DEBUG_OPTIONS'])
        self.assertIn('Oculta', entries['DLSSIndicator=0'])

    def test_error_does_not_describe_partial_command_as_valid(self):
        entries = explain_result(generate(Config(gpu='rtx50', smooth='on', fg_mode='on')))
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0][0], 'Comando no disponible')

    def test_epic_arguments_never_include_environment_or_steam_marker(self):
        self.assertEqual(epic_arguments('NVPRESENT_ENABLE_SMOOTH_MOTION=1 %command% -dx12'), '-dx12')
        self.assertEqual(epic_arguments(''), '')
        with self.assertRaises(ValueError):
            epic_arguments('gamescope -- %command% -dx12')
        with self.assertRaises(ValueError):
            epic_arguments('%command% ; echo invalid')
