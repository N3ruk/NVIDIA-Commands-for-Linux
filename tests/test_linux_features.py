import shlex
import unittest
from nvidia_commands.core import Config, Selection, generate

class LinuxFeatureTests(unittest.TestCase):
    def config(self, **kw):
        return Config(gpu='rtx50', driver='595.99.02', smooth_layer=True, reflex_layer=True, **kw)
    def ok(self, **kw):
        r = generate(self.config(**kw))
        self.assertFalse(r.errors, r.errors)
        return r
    def bad(self, **kw):
        r = generate(self.config(**kw))
        self.assertTrue(r.errors)
        self.assertEqual(r.command, '')
        return r
    def test_smooth_motion(self):
        r = self.ok(smooth='on')
        self.assertEqual(r.environment['NVPRESENT_ENABLE_SMOOTH_MOTION'], '1')
        self.assertTrue(any('desactiva FG' in w for w in r.warnings))
    def test_smooth_motion_unsupported_gpu(self):
        for family in ['rtx20','rtx30','unknown']:
            c = self.config(smooth='on'); c.gpu = family
            self.assertTrue(generate(c).errors)
    def test_smooth_layer_and_driver(self):
        for attr, val in [('smooth_layer',False),('driver','570.1'),('driver','unknown')]:
            c = self.config(smooth='on');setattr(c,attr,val)
            self.assertTrue(generate(c).errors)
    def test_smooth_rejects_opengl(self):
        self.bad(smooth='on',api='opengl',sr=Selection())
    def test_smooth_fg_conflicts(self):
        for mode in ['on','dynamic']:
            self.bad(smooth='on',fg_mode=mode)
            self.bad(fg_mode=mode,existing='NVPRESENT_ENABLE_SMOOTH_MOTION=1 %command%')
    def test_smooth_checks_existing_fg(self):
        self.bad(smooth='on',existing='DXVK_NVAPI_DRS_NGX_DLSSG_MODE=on %command%')
        self.bad(smooth='on',existing='DXVK_NVAPI_DRS_SETTINGS=NGX_DLSS_FG_OVERRIDE=on %command%')
    def test_smooth_explicit_fg_off(self):
        self.ok(smooth='on',fg_mode='off',fg=Selection('latest'))
    def test_smooth_overlay_queue(self):
        self.assertEqual(self.ok(smooth='on',smooth_queue=True).environment['NVPRESENT_QUEUE_FAMILY'],'1')
        self.bad(smooth_queue=True)
    def test_reflex_bridge(self):
        self.assertEqual(self.ok(api='vulkan',reflex=True).environment['DXVK_NVAPI_VKREFLEX'],'1')
        self.bad(reflex=True)
        c=self.config(api='vulkan',reflex=True);c.reflex_layer=False
        self.assertTrue(generate(c).errors)
    def test_fps_selects_correct_backend(self):
        self.assertIn('dxgi.maxFrameRate = 144',self.ok(fps=144).environment['DXVK_CONFIG'])
        r=self.ok(api='dx12',fps=120)
        self.assertEqual(r.environment['VKD3D_FRAME_RATE'],'120')
        self.assertNotIn('DXVK_CONFIG',r.environment)
        for api in ['vulkan','opengl']:self.bad(api=api,sr=Selection(),fps=120)
        for n in [-1,1001]:self.bad(fps=n)
    def test_dxvk_merges_unrelated_options(self):
        r=self.ok(vsync='on',anisotropy=16,existing='DXVK_CONFIG="dxgi.hideNvidiaGpu = False; dxgi.syncInterval = 0" %command%')
        self.assertIn('dxgi.hideNvidiaGpu = False',r.environment['DXVK_CONFIG'])
        self.assertIn('dxgi.syncInterval = 1',r.environment['DXVK_CONFIG'])
        self.assertEqual(r.environment['DXVK_CONFIG'].count('dxgi.syncInterval'),1)
        self.bad(vsync='on',existing='DXVK_CONFIG=invalid %command%')
    def test_dx12_does_not_get_dxvk_settings(self):
        for kw in [dict(vsync='on'),dict(anisotropy=16),dict(lod_bias='-0.5'),dict(low_latency='on'),dict(hdr=True),dict(hud='dxvk')]:self.bad(api='dx12',**kw)
    def test_opengl_values(self):
        r=self.ok(api='opengl',sr=Selection(),vsync='off',anisotropy=16,gl_vrr='on',gl_threaded='on',gl_cache='off',gl_fxaa='off')
        self.assertEqual(r.environment['__GL_SYNC_TO_VBLANK'],'0')
        self.assertEqual(r.environment['__GL_LOG_MAX_ANISO'],'4')
        self.assertEqual(r.environment['__GL_VRR_ALLOWED'],'1')
        self.assertEqual(r.environment['__GL_SHADER_DISK_CACHE'],'0')
        self.assertNotIn('DXVK_CONFIG',r.environment)
    def test_opengl_settings_rejected_on_vulkan(self):
        for key in ['gl_vrr','gl_threaded','gl_cache','gl_fxaa']:self.bad(**{key:'on'})
    def test_sharpening(self):
        for api in ['dxvk','dx12','vulkan','opengl']:
            r=self.ok(api=api,sr=Selection(),sharpen='on',sharpen_value=75,film_grain=20)
            self.assertEqual(r.environment['__GL_SHARPEN_VALUE'],'75')
        self.bad(sharpen='on',sharpen_value=101)
        c=self.config(sharpen='on');c.driver='580.1'
        self.assertTrue(generate(c).errors)
    def test_low_latency_and_hdr(self):
        r=self.ok(low_latency='on',hdr=True)
        self.assertEqual(r.environment['DXVK_HDR'],'1')
        self.assertIn('dxvk.latencySleep = True',r.environment['DXVK_CONFIG'])
        self.assertTrue(any('No es RTX HDR' in w for w in r.warnings))
    def test_hud_preserves_existing_metrics(self):
        r=self.ok(hud='dxvk',existing='DXVK_HUD=devinfo,fps %command%')
        self.assertIn('devinfo',r.environment['DXVK_HUD'])
        self.assertEqual(r.environment['DXVK_HUD'].count('fps'),1)
    def test_indicators_can_be_cleared_and_preserve_other_keys(self):
        r=self.ok(indicator='off',existing='DXVK_NVAPI_SET_NGX_DEBUG_OPTIONS=OtherKey=7 %command%')
        self.assertIn('DLSSIndicator=0,DLSSGIndicator=0',r.environment['DXVK_NVAPI_SET_NGX_DEBUG_OPTIONS'])
        self.assertIn('OtherKey=7',r.environment['DXVK_NVAPI_SET_NGX_DEBUG_OPTIONS'])
        self.assertTrue(any('persiste' in w for w in r.warnings))
    def test_prime_and_api_osd(self):
        r=self.ok(prime=True,api_osd=True)
        self.assertEqual(r.environment['__NV_PRIME_RENDER_OFFLOAD'],'1')
        self.assertEqual(r.environment['__GL_SHOW_GRAPHICS_OSD'],'1')
    def test_previous_dynamic_settings_removed_when_fixed_requested(self):
        r=self.ok(fg_mode='on',existing='DXVK_NVAPI_DRS_SETTINGS=NGX_DLSSG_DYNAMIC_TARGET_FRAME_RATE=240,NGX_DLSSG_DYNAMIC_MULTI_FRAME_COUNT_MAX=5 %command%')
        self.assertNotIn('DYNAMIC_',r.command)
        self.assertIn('NGX_DLSSG_MULTI_FRAME_COUNT=1',r.command)
    def test_epic_has_no_steam_placeholder(self):
        r=self.ok(launcher='epic',epic_path='/home/user/Epic Games.AppImage')
        tokens=shlex.split(r.command)
        self.assertEqual(tokens[0],'env')
        self.assertEqual(tokens[-1],'/home/user/Epic Games.AppImage')
        self.assertNotIn('%command%',r.command)
        self.assertTrue(any('toda esa sesión' in w for w in r.warnings))
    def test_epic_game_arguments_are_separate(self):
        r=self.ok(launcher='epic',epic_path='/opt/epic',epic_uri='com.epicgames.launcher://apps/test?action=launch&silent=true',existing='%command% -dx12 -language "es ES"')
        self.assertEqual(shlex.split(r.game_arguments),['-dx12','-language','es ES'])
        self.assertNotIn('-dx12',r.command)
        self.assertIn('com.epicgames.launcher://apps/',shlex.split(r.command)[-1])
    def test_epic_rejects_steam_wrappers(self):
        self.bad(launcher='epic',epic_path='/opt/epic',existing='gamescope -- %command%')
    def test_epic_requires_absolute_path(self):
        for p in ['', 'relative/Epic.AppImage']:self.bad(launcher='epic',epic_path=p)
    def test_epic_uri_validation_and_path_quoting(self):
        self.bad(launcher='epic',epic_path='/opt/epic',epic_uri='https://example.com/')
        r=self.ok(launcher='epic',epic_path='/tmp/$(touch never).AppImage')
        self.assertEqual(shlex.split(r.command)[-1],'/tmp/$(touch never).AppImage')
    def test_steam_assignment_shell_grammar(self):
        r=self.ok(existing='FOO="a b" %command%')
        self.assertIn("FOO='a b'",r.command)
        self.assertNotIn("'FOO=a b'",r.command)
    def test_no_extra_environment_by_default(self):
        self.assertEqual(self.ok(sr=Selection()).command,'%command%')

class NativeAndScalingTests(unittest.TestCase):
    def test_native_vulkan_never_uses_proton_overrides(self):
        c=Config(gpu='rtx50',api='native_vulkan',sr=Selection(),indicator='on',smooth='on',driver='595.99',smooth_layer=True)
        r=generate(c)
        self.assertFalse(r.errors,r.errors)
        self.assertEqual(r.environment['__NGX_SHOW_INDICATOR'],'1024')
        self.assertNotIn('PROTON_ENABLE_NGX_UPDATER',r.command)
        self.assertNotIn('DXVK_NVAPI_',r.command)
        self.assertTrue(generate(Config(api='native_vulkan')).errors)
    def test_workstation_name_not_misidentified_as_blackwell(self):
        from nvidia_commands.core import family_for
        self.assertEqual(family_for('NVIDIA RTX 5000 Ada Generation'),'unknown')
        self.assertEqual(family_for('NVIDIA GeForce RTX 5070 Ti'),'rtx50')
    def test_nis_and_supersampling(self):
        for mode,size,required in [('nis','720-1080','-F nis'),('fsr','1440-4k','-F fsr'),('supersample','4k-1440','-w 3840 -h 2160 -W 2560 -H 1440')]:
            r=generate(Config(gamescope=mode,scaling_size=size))
            self.assertFalse(r.errors,r.errors)
            self.assertIn(required,r.command)
            self.assertEqual(r.command.count('%command%'),1)
        for mode,size in [('nis','4k-1080'),('supersample','720-1080')]:self.assertTrue(generate(Config(gamescope=mode,scaling_size=size)).errors)
    def test_no_nested_gamescope_or_epic_launcher_wrapper(self):
        self.assertTrue(generate(Config(gamescope='nis',existing='gamescope -- %command%')).errors)
        self.assertTrue(generate(Config(gamescope='nis',launcher='epic',epic_path='/opt/epic')).errors)
    def test_posix_shell_receives_environment_assignments(self):
        import subprocess
        r=generate(Config(existing='FOO="two words" %command%',fps=60))
        self.assertFalse(r.errors)
        result=subprocess.run(['/bin/sh','-c',r.command.replace('%command%','/usr/bin/env')],env={'PATH':'/usr/bin:/bin'},capture_output=True,text=True,check=True)
        env=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
        self.assertEqual(env['FOO'],'two words')
        self.assertIn('dxgi.maxFrameRate = 60',env['DXVK_CONFIG'])

class CustomScaleTests(unittest.TestCase):
    def test_custom_ratio_and_dynamic_mode(self):
        r=generate(Config(gpu='rtx50',sr=Selection('K','custom',75),rr=Selection('game','custom',90),fg_mode='dynamic'))
        self.assertFalse(r.errors,r.errors)
        self.assertEqual(r.settings['NGX_DLSS_SR_OVERRIDE_SCALING_RATIO'],'75')
        self.assertEqual(r.settings['NGX_DLSS_RR_OVERRIDE_SCALING_RATIO'],'90')
        self.assertEqual(r.settings['NGX_DLSSG_MODE'],'dynamic')
        self.assertTrue(generate(Config(sr=Selection('K','custom',0))).errors)
        self.assertTrue(generate(Config(sr=Selection('K','custom',101))).errors)
    def test_imported_dynamic_mode_conflicts_with_smooth_motion(self):
        for value in ['dynamic','4','0x4']:
            r=generate(Config(gpu='rtx50',smooth='on',existing='DXVK_NVAPI_DRS_SETTINGS=NGX_DLSSG_MODE='+value+' %command%'))
            self.assertTrue(r.errors)

class DriverBaselineTests(unittest.TestCase):
    def test_smooth_motion_driver_baselines(self):
        from nvidia_commands.core import smooth_driver_supported
        for family,version,expected in [('rtx50','580.65.06',True),('rtx50','580.65.05',False),('rtx40','580.65.06',False),('rtx40','580.95.05',True),('rtx40','595.99.02',True),('rtx50','invalid',False)]:
            self.assertEqual(smooth_driver_supported(family,version),expected)
    def test_custom_scale_below_documented_minimum_rejected(self):
        self.assertTrue(generate(Config(sr=Selection('K','custom',32))).errors)
        self.assertFalse(generate(Config(sr=Selection('K','custom',33))).errors)
    def test_smooth_is_not_enabled_on_gamescope_compositor(self):
        self.assertTrue(generate(Config(gpu='rtx50',gamescope='nis',smooth='on')).errors)
