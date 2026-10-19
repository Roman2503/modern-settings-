# -*- coding: utf-8 -*-
"""Modern Settings - Gameface version for Mir Tankov."""

from __future__ import absolute_import

import json
import traceback

import BigWorld
import Keys
import CommandMapping

from helpers import dependency

try:
    from gui import InputHandler
except Exception:
    InputHandler = None

from gui.impl.pub import ViewImpl, WindowImpl
from frameworks.wulf import ViewModel, ViewSettings, ViewFlags, WindowFlags
from openwg_gameface import ModDynAccessor


TAG = '[ModernSettings]'
VERSION = 'GF-2.2'
WINDOW_MODE = 'fullscreen'
RES_MAP_ITEM_ID = 'MODERN_SETTINGS_WINDOW'

SENSITIVITY_KEYS = (
    'mouseArcadeSens',
    'mouseSniperSens',
    'mouseStrategicSens',
    'mouseFreeCamSens',
)

# Альтернативные имена ключей в ISettingsCore (ключ UI -> кортеж возможных имён в клиенте)
SETTING_KEY_ALIASES = {
    'musicVolume': ('music', 'musicVolume'),
    'artilleryBulbVoices': ('artyBulbVoices', 'artilleryBulbVoices'),
    'dynamicRenderer': ('dynamicRenderer', 'DynamicRenderer'),
}

# Команды управления из CommandMapping (ключ в UI -> (список кандидатов команд в CommandMapping, клавиша по умолчанию))
KEYBIND_COMMANDS = {
    'bind_CMD_MOVE_FORWARD': (('CMD_MOVE_FORWARD',), 'KEY_W'),
    'bind_CMD_MOVE_BACKWARD': (('CMD_MOVE_BACKWARD',), 'KEY_S'),
    'bind_CMD_ROTATE_LEFT': (('CMD_ROTATE_LEFT',), 'KEY_A'),
    'bind_CMD_ROTATE_RIGHT': (('CMD_ROTATE_RIGHT',), 'KEY_D'),
    'bind_CMD_INCREMENT_CRUISE_MODE': (('CMD_INCREMENT_CRUISE_MODE',), 'KEY_R'),
    'bind_CMD_DECREMENT_CRUISE_MODE': (('CMD_DECREMENT_CRUISE_MODE',), 'KEY_F'),
    'bind_CMD_STOP_UNTIL_FIRE': (('CMD_STOP_UNTIL_FIRE',), 'KEY_SPACE'),
    'bind_CMD_BLOCK_TRACKS': (('CMD_BLOCK_TRACKS',), 'KEY_SPACE'),
    'bind_CMD_CM_VEHICLE_SWITCH_AUTOROTATION': (('CMD_CM_VEHICLE_SWITCH_AUTOROTATION',), 'KEY_X'),
    'bind_CMD_CM_SHOOT': (('CMD_CM_SHOOT',), 'KEY_LEFTMOUSE'),
    'bind_CMD_CM_ALTERNATE_MODE': (('CMD_CM_ALTERNATE_MODE',), 'KEY_LSHIFT'),
    'bind_CMD_CM_LOCK_TARGET': (('CMD_CM_LOCK_TARGET',), 'KEY_RIGHTMOUSE'),
    'bind_CMD_CM_LOCK_TARGET_OFF': (('CMD_CM_LOCK_TARGET_OFF',), 'KEY_E'),
    'bind_CMD_CM_TRAJECTORY_VIEW': (('CMD_CM_TRAJECTORY_VIEW',), 'KEY_G'),
    'bind_CMD_RELOAD_PARTIAL_CLIP': (('CMD_RELOAD_PARTIAL_CLIP',), 'KEY_C'),
    'bind_CMD_AMMO_CHOICE_1': (('CMD_AMMO_CHOICE_1',), 'KEY_1'),
    'bind_CMD_AMMO_CHOICE_2': (('CMD_AMMO_CHOICE_2',), 'KEY_2'),
    'bind_CMD_AMMO_CHOICE_3': (('CMD_AMMO_CHOICE_3',), 'KEY_3'),
    'bind_CMD_AMMO_CHOICE_4': (('CMD_AMMO_CHOICE_4',), 'KEY_4'),
    'bind_CMD_AMMO_CHOICE_5': (('CMD_AMMO_CHOICE_5',), 'KEY_5'),
    'bind_CMD_AMMO_CHOICE_6': (('CMD_AMMO_CHOICE_6',), 'KEY_6'),
    'bind_CMD_RADIAL_MENU_SHOW': (('CMD_RADIAL_MENU_SHOW',), 'KEY_Z'),
    'bind_CMD_CHAT_SHORTCUT_COMMON_COMMAND': (
        ('CMD_CHAT_SHORTCUT_CONTEXT_COMMAND', 'CMD_CHAT_SHORTCUT_COMMON_COMMAND', 'CMD_CHAT_SHORTCUT_ATTACK'),
        'KEY_T'
    ),
    'bind_CMD_VOICECHAT_MUTE': (('CMD_VOICECHAT_MUTE',), 'KEY_Q'),
    'bind_CMD_TOGGLE_GUI': (('CMD_TOGGLE_GUI',), 'KEY_V'),
    'bind_CMD_MINIMAP_SIZE_UP': (('CMD_MINIMAP_SIZE_UP',), 'KEY_EQUALS'),
    'bind_CMD_MINIMAP_SIZE_DOWN': (('CMD_MINIMAP_SIZE_DOWN',), 'KEY_MINUS'),
    'bind_CMD_MINIMAP_VISIBLE': (('CMD_MINIMAP_VISIBLE',), 'KEY_M'),
}

SETTINGS_DEFAULTS = {
    # --- ВКЛАДКА: ИГРА ---
    'dynamicCamera': True,
    'horStabilizationSnp': True,
    'increasedZoom': True,
    'sniperModeByShift': True,
    'enableOpticalSnpEffect': True,
    'useServerAim': False,
    'preCommanderCam': True,
    'commanderCam': True,
    'hullLockEnabled': True,
    'postMortemMode': True,
    'dynamicFov': False,
    'minimapAlphaEnabled': False,
    'minimapAlpha': 0,
    'minimapViewRange': True,
    'minimapMaxViewRange': True,
    'minimapDrawRange': True,
    'minimapMinSpottingRange': False,
    'showVehModelsOnMap': 0,
    'showVectorOnMap': False,
    'showSectorOnMap': True,
    'showVehicleHPinMinimap': 1,
    'showVehicleHPinPlayersPanel': 1,
    'showDamageIcon': True,
    'enableSpeedometer': True,
    'enableRepairTimer': True,
    'showMarksOnGun': False,
    'c11nHistoricallyAccurate': False,
    'disableBattleChat': False,
    'chatContactsListOnly': False,
    'receiveFriendshipRequest': True,
    'receiveInvitesInBattle': True,
    'replayEnabled': 2,
    'carouselType': 1,
    'doubleCarouselType': 0,
    'vehicleCarouselStats': True,
    'hangarCamPeriod': 0,
    'hangarCamParallaxEnabled': True,

    # --- ВКЛАДКА: ГРАФИКА ---
    'RENDER_PIPELINE': 0,
    'vertSync': False,
    'tripleBuffered': True,
    'isColorBlind': False,
    'dynamicRenderer': 100,
    'DRR_AUTOSCALER_ENABLED': False,
    'TEXTURE_QUALITY': 0,
    'SHADOWS_QUALITY': 0,
    'LIGHTING_QUALITY': 0,
    'POST_PROCESSING_QUALITY': 0,
    'MOTION_BLUR_QUALITY': 3,
    'TERRAIN_QUALITY': 0,
    'WATER_QUALITY': 0,
    'FLORA_QUALITY': 0,
    'EFFECTS_QUALITY': 0,
    'OBJECT_LOD': 0,
    'SNIPER_MODE_GRASS_ENABLED': False,
    'SNIPER_MODE_EFFECTS_QUALITY': 0,
    'VEHICLE_DUST_ENABLED': True,
    'VEHICLE_TRACES_ENABLED': True,
    'SEMITRANSPARENT_LEAVES_ENABLED': True,
    'TERRAIN_TESSELLATION_ENABLED': False,
    'SNIPER_MODE_TERRAIN_TESSELLATION_ENABLED': False,

    # --- ВКЛАДКА: ЗВУК ---
    'masterVolumeToggle': True,
    'masterVolume': 80,
    'musicVolume': 60,
    'musicHangar': 60,
    'voiceNotification': 80,
    'vehicles': 80,
    'effects': 80,
    'gui': 80,
    'ambient': 80,
    'soundQuality': 0,
    'subtitles': False,
    'bassBoost': False,
    'nightMode': False,
    'altVoices': 0,
    'bulbVoices': 0,
    'artilleryBulbVoices': 0,
    'enableVoIP': False,
    'masterVivoxVolume': 80,
    'micVivoxVolume': 80,

    # --- ВКЛАДКА: УПРАВЛЕНИЕ ---
    'mouseArcadeSens': 50,
    'mouseSniperSens': 50,
    'mouseStrategicSens': 50,
    'mouseFreeCamSens': 50,
    'mouseHorzInvert': False,
    'mouseVertInvert': False,
    'backDraftInvert': False,
}

g_state = {
    'fovTuple': (120, 80.0, 100.0),
    'settings': dict(SETTINGS_DEFAULTS, fovStatic=100, fovMin=80, fovMax=120),
    'rawTypes': {},
    'realKeyMap': {},
    'resolvedBinds': {},
    'supportedKeys': [],
    'useLegacySettings': False,
    'bypassHookOnce': False,
    'pageReady': False,
    'listeningBind': None,
    'captureSeq': 0,
    'seenMsgIds': set(),
}

g_window = None


def _to_text(value):
    try:
        if isinstance(value, unicode):
            return value.encode('utf-8')
    except NameError:
        pass
    return str(value)


def _clean_unicode(obj):
    try:
        if isinstance(obj, unicode):
            return obj.encode('utf-8')
    except NameError:
        pass
    if isinstance(obj, dict):
        res = {}
        for k, v in obj.items():
            res[_clean_unicode(k)] = _clean_unicode(v)
        return res
    if isinstance(obj, list):
        return [_clean_unicode(x) for x in obj]
    return obj


def dlog(message):
    try:
        with open('modern_settings_debug.txt', 'ab') as stream:
            stream.write(_to_text(message) + '\r\n')
    except Exception:
        pass


def log(message, level='info'):
    message = _to_text(message)
    dlog(message)
    try:
        from gui import SystemMessages
        names = {'info': 'Information', 'warn': 'Warning', 'err': 'Error'}
        msg_type = getattr(SystemMessages.SM_TYPE, names.get(level, 'Information'))
        SystemMessages.pushMessage('%s %s' % (TAG, message), type=msg_type)
    except Exception:
        pass


def _is_plain(value):
    return isinstance(value, (bool, int, float))


def _key_code_to_name(key_code):
    try:
        if not key_code or int(key_code) == 0:
            return 'KEY_NONE'
        name = BigWorld.keyToString(int(key_code))
        if name:
            return str(name)
    except Exception:
        pass
    return 'KEY_NONE'


def _read_raw_setting(settings_core, ui_key):
    candidates = SETTING_KEY_ALIASES.get(ui_key, (ui_key,))
    for candidate in candidates:
        try:
            val = settings_core.getSetting(candidate)
            if val is not None:
                return candidate, val
        except Exception:
            pass

    # Резервное чтение графических настроек напрямую через модуль graphics
    try:
        from gui.shared.utils import graphics
        for candidate in candidates:
            g_opt = graphics.getGraphicsSetting(candidate)
            if g_opt is not None and getattr(g_opt, 'value', None) is not None:
                return candidate, g_opt.value
    except Exception:
        pass

    return ui_key, None


def read_settings_from_core():
    try:
        from skeletons.account_helpers.settings_core import ISettingsCore
        settings_core = dependency.instance(ISettingsCore)

        current = {}
        supported = []
        raw_types = {}
        real_key_map = {}
        resolved_binds = {}

        try:
            fov = settings_core.getSetting('fov')
        except Exception:
            fov = None

        if isinstance(fov, (tuple, list)) and len(fov) == 3:
            g_state['fovTuple'] = tuple(fov)
            current['fovMax'] = int(round(float(fov[0])))
            current['fovMin'] = int(round(float(fov[1])))
            current['fovStatic'] = int(round(float(fov[2])))
            supported.extend(['fovStatic', 'fovMin', 'fovMax'])
        else:
            current['fovMax'] = 120
            current['fovMin'] = 80
            current['fovStatic'] = 100

        for key, default_value in SETTINGS_DEFAULTS.items():
            real_key, value = _read_raw_setting(settings_core, key)
            real_key_map[key] = real_key

            if value is not None and _is_plain(value):
                raw_types[key] = type(value)
                if key in SENSITIVITY_KEYS:
                    current[key] = max(1, min(100, int(round(float(value) * 100.0))))
                elif isinstance(value, bool):
                    current[key] = bool(value)
                elif key == 'minimapAlpha':
                    # В клиенте minimapAlpha может храниться как 0..100 или 0.0..100.0
                    current[key] = max(0, min(100, int(round(float(value)))))
                elif isinstance(value, float):
                    current[key] = int(round(value))
                else:
                    current[key] = value
                supported.append(key)
            elif value is not None and isinstance(value, basestring) and key == 'altVoices':
                raw_types[key] = str
                current[key] = 0 if str(value) in ('default', '0', '') else 1
                supported.append(key)
            else:
                current[key] = default_value

        # Читаем привязки клавиш из CommandMapping.g_instance
        cmd_map = getattr(CommandMapping, 'g_instance', None)
        for ui_key, (cmd_candidates, default_key_str) in KEYBIND_COMMANDS.items():
            if isinstance(cmd_candidates, basestring):
                cmd_candidates = (cmd_candidates,)
            matched_cmd = None
            if cmd_map is not None:
                for cand in cmd_candidates:
                    if hasattr(CommandMapping, cand):
                        matched_cmd = cand
                        break
            if matched_cmd is not None:
                resolved_binds[ui_key] = matched_cmd
                try:
                    key_code = cmd_map.get(matched_cmd)
                    current[ui_key] = _key_code_to_name(key_code)
                    supported.append(ui_key)
                except Exception:
                    current[ui_key] = default_key_str
            else:
                current[ui_key] = default_key_str

        g_state['settings'] = current
        g_state['rawTypes'] = raw_types
        g_state['realKeyMap'] = real_key_map
        g_state['resolvedBinds'] = resolved_binds
        g_state['supportedKeys'] = supported
        dlog('Прочитано настроек: %d' % len(supported))
    except Exception:
        traceback.print_exc()
        log('Ошибка чтения настроек: %s' % traceback.format_exc(), 'err')


def _coerce_for_core(key, ui_value, raw_types):
    if key in SENSITIVITY_KEYS:
        return max(0.01, min(1.0, float(ui_value) / 100.0))

    expected_type = raw_types.get(key)
    if expected_type is bool:
        return bool(ui_value)
    if expected_type is float:
        return float(ui_value)
    if expected_type is int:
        return int(round(float(ui_value)))

    if isinstance(ui_value, bool):
        return bool(ui_value)
    if isinstance(ui_value, (int, float)):
        return ui_value
    return ui_value


def apply_settings_to_core(new_data):
    try:
        from skeletons.account_helpers.settings_core import ISettingsCore
        settings_core = dependency.instance(ISettingsCore)

        new_data = _clean_unicode(new_data or {})
        diff = {}
        bind_diff = {}
        current = g_state.get('settings', {})
        supported = set(g_state.get('supportedKeys', []))
        raw_types = g_state.get('rawTypes', {})
        real_key_map = g_state.get('realKeyMap', {})
        resolved_binds = g_state.get('resolvedBinds', {})

        # 1. FOV
        old_fov = g_state.get('fovTuple', (120, 80.0, 100.0))
        fov_changed = False
        for f_key in ('fovStatic', 'fovMin', 'fovMax'):
            if f_key in supported and f_key in new_data:
                if int(round(float(new_data[f_key]))) != int(round(float(current.get(f_key, 100)))):
                    fov_changed = True

        dyn_fov_changed = (
            'dynamicFov' in supported and
            'dynamicFov' in new_data and
            bool(new_data['dynamicFov']) != bool(current.get('dynamicFov', False))
        )

        if fov_changed or dyn_fov_changed:
            f_max = int(round(float(new_data.get('fovMax', current.get('fovMax', old_fov[0])))))
            f_min = float(new_data.get('fovMin', current.get('fovMin', old_fov[1])))
            f_stat = float(new_data.get('fovStatic', current.get('fovStatic', old_fov[2])))
            if f_min > f_max:
                f_min = float(f_max)
            diff['fov'] = (f_max, f_min, f_stat)
            diff['dynamicFov'] = bool(new_data.get('dynamicFov', current.get('dynamicFov', False)))

        # 2. Остальные параметры и клавиши
        for key in supported:
            if key in ('fovStatic', 'fovMin', 'fovMax', 'dynamicFov'):
                continue
            if key not in new_data:
                continue
            if new_data[key] != current.get(key):
                if key.startswith('bind_'):
                    bind_diff[key] = str(new_data[key])
                else:
                    real_key = real_key_map.get(key, key)
                    diff[real_key] = _coerce_for_core(key, new_data[key], raw_types)

        if 'minimapAlpha' in diff or 'minimapAlphaEnabled' in diff:
            if 'minimapAlpha' in supported:
                rk_alpha = real_key_map.get('minimapAlpha', 'minimapAlpha')
                diff[rk_alpha] = _coerce_for_core(
                    'minimapAlpha',
                    new_data.get('minimapAlpha', current.get('minimapAlpha', 0)),
                    raw_types)
            if 'minimapAlphaEnabled' in supported:
                rk_alpha_en = real_key_map.get('minimapAlphaEnabled', 'minimapAlphaEnabled')
                diff[rk_alpha_en] = bool(
                    new_data.get('minimapAlphaEnabled', current.get('minimapAlphaEnabled', False)))

        total_changed = len(diff) + len(bind_diff)
        dlog('apply: diff=%s, binds=%s' % (repr(list(diff.keys())), repr(bind_diff)))

        if diff:
            try:
                settings_core.clearStorages()
            except Exception:
                pass

            try:
                settings_core.applySettings(diff)
            except Exception as bulk_exc:
                dlog('applySettings fallback: %s' % bulk_exc)
                for k, v in diff.items():
                    try:
                        settings_core.applySetting(k, v)
                    except Exception as key_exc:
                        dlog('applySetting(%s) error: %s' % (k, key_exc))

            try:
                confirmators = settings_core.applyStorages(restartApproved=True)
                settings_core.confirmChanges(confirmators)
            except Exception as st_exc:
                dlog('applyStorages error: %s' % st_exc)

            try:
                BigWorld.commitPendingGraphicsSettings()
            except Exception:
                pass

            try:
                settings_core.clearStorages()
            except Exception:
                pass

        # 3. Применение переназначенных клавиш через CommandMapping
        if bind_diff:
            cmd_map = getattr(CommandMapping, 'g_instance', None)
            if cmd_map is not None:
                for ui_key, new_key_str in bind_diff.items():
                    cmd_name = resolved_binds.get(ui_key)
                    if not cmd_name:
                        cmd_info = KEYBIND_COMMANDS.get(ui_key)
                        if not cmd_info:
                            continue
                        cands = cmd_info[0]
                        cmd_name = cands[0] if isinstance(cands, (tuple, list)) else cands
                    try:
                        cmd_map.remove(cmd_name)
                        if new_key_str and new_key_str != 'KEY_NONE':
                            cmd_map.add(cmd_name, str(new_key_str))
                        if cmd_name == 'CMD_MOVE_FORWARD':
                            cmd_map.remove('CMD_MOVE_FORWARD_SPEC')
                            if new_key_str and new_key_str != 'KEY_NONE':
                                cmd_map.add('CMD_MOVE_FORWARD_SPEC', str(new_key_str))
                    except Exception as b_exc:
                        dlog('CommandMapping error (%s -> %s): %s' % (cmd_name, new_key_str, b_exc))
                try:
                    cmd_map.save()
                except Exception:
                    pass
                try:
                    cmd_map.onMappingChanged()
                except Exception:
                    pass

        if total_changed > 0:
            try:
                import Settings
                Settings.g_instance.save()
            except Exception:
                pass

            read_settings_from_core()
            log('Сохранено и применено параметров: %d' % total_changed)

        return True
    except Exception as exc:
        log('Ошибка применения: %s: %s' % (type(exc).__name__, exc), 'err')
        traceback.print_exc()
        return False


def _state_payload():
    return json.dumps({
        'settings': g_state.get('settings', {}),
        'supported': g_state.get('supportedKeys') or None
    }, ensure_ascii=True, separators=(',', ':'))


def _as_dict(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, basestring):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None
    try:
        return dict(value.items())
    except Exception:
        pass
    res = {}
    for k in ('id', 'cmd', 'json', 'data'):
        try:
            v = value.get(k) if hasattr(value, 'get') else getattr(value, k, None)
            if v is not None:
                res[k] = v
        except Exception:
            pass
    return res if res else None


class ModernSettingsViewModel(ViewModel):
    def __init__(self):
        super(ModernSettingsViewModel, self).__init__(properties=2, commands=1)

    def _initialize(self):
        super(ModernSettingsViewModel, self)._initialize()
        self._addStringProperty('stateJson', _state_payload())
        self._addStringProperty('ackJson', '')
        self._apiRequest = self._addCommand('apiRequest')
        self._apiRequest += self._on_api_request

    @property
    def stateJson(self):
        return self._getString(0)

    @stateJson.setter
    def stateJson(self, value):
        self._setString(0, value)

    @property
    def ackJson(self):
        return self._getString(1)

    @ackJson.setter
    def ackJson(self, value):
        self._setString(1, value)

    def send_ack(self, message_id, ok, extra=None):
        data = {'id': _to_text(message_id), 'ok': bool(ok)}
        if isinstance(extra, dict):
            data.update(extra)
        payload = json.dumps(data, ensure_ascii=True, separators=(',', ':'))
        try:
            with self.transaction() as tx:
                tx.ackJson = payload
        except Exception:
            self.ackJson = payload

    def publish_state(self):
        payload = _state_payload()
        try:
            with self.transaction() as tx:
                tx.stateJson = payload
        except Exception:
            self.stateJson = payload

    def handle_command_payload(self, message_id, command, data):
        try:
            message_id = _to_text(message_id or '')
            command = _to_text(command or '')

            if message_id:
                seen = g_state['seenMsgIds']
                if message_id in seen:
                    return
                seen.add(message_id)
                if len(seen) > 500:
                    seen.clear()

            if not isinstance(data, dict):
                data = {}

            if command == 'hello':
                g_state['pageReady'] = True
                self.publish_state()
                self.send_ack(message_id, True)
                return

            if command == 'listen_key':
                target = _to_text(data.get('key', ''))
                g_state['listeningBind'] = target if target else None
                self.send_ack(message_id, True)
                return

            if command == 'log':
                dlog('JS: %s' % _to_text(data.get('msg', '')))
                self.send_ack(message_id, True)
                return

            if command == 'apply':
                ok = apply_settings_to_core(data)
                self.publish_state()
                self.send_ack(message_id, ok)
                return

            if command == 'use_legacy':
                self.send_ack(message_id, True)
                BigWorld.callback(
                    0.05,
                    lambda: switch_to_legacy_settings(
                        bool(data.get('permanent', True))))
                return

            if command == 'close':
                self.send_ack(message_id, True)
                BigWorld.callback(0.01, close_custom_window)
                return

        except Exception:
            traceback.print_exc()

    def _on_api_request(self, args=None):
        try:
            parsed = _as_dict(args)
            if not parsed:
                return
            message_id = parsed.get('id', '')
            command = parsed.get('cmd', '')
            raw_json = parsed.get('json')
            if raw_json and isinstance(raw_json, basestring):
                data = _as_dict(raw_json) or {}
            else:
                data = _as_dict(parsed.get('data', {})) or {}

            self.handle_command_payload(message_id, command, data)
        except Exception:
            traceback.print_exc()


class ModernSettingsView(ViewImpl):
    viewLayoutID = ModDynAccessor(RES_MAP_ITEM_ID)

    def __init__(self, model):
        settings = ViewSettings(
            ModernSettingsView.viewLayoutID(),
            flags=ViewFlags.VIEW,
            model=model
        )
        super(ModernSettingsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ModernSettingsView, self).getViewModel()

    def createToolTip(self, event):
        try:
            cmd = event.getArgument('cmd', '')
            if cmd:
                msg_id = event.getArgument('id', '')
                raw_json = event.getArgument('json', '{}')
                data = _as_dict(raw_json) or {}
                self.viewModel.handle_command_payload(msg_id, cmd, data)
                return None
        except Exception:
            traceback.print_exc()
        return super(ModernSettingsView, self).createToolTip(event)


def _window_flags():
    flags = WindowFlags.WINDOW
    if WINDOW_MODE == 'fullscreen':
        fullscreen = getattr(WindowFlags, 'WINDOW_FULLSCREEN', None)
        if fullscreen is not None:
            try:
                flags = WindowFlags.WINDOW | fullscreen
            except Exception:
                flags = fullscreen
    return flags


class ModernSettingsWindow(WindowImpl):
    def __init__(self):
        self.model = ModernSettingsViewModel()
        content = ModernSettingsView(self.model)

        super(ModernSettingsWindow, self).__init__(
            wndFlags=_window_flags(),
            content=content
        )


def close_custom_window():
    global g_window
    g_state['listeningBind'] = None
    try:
        if g_window is not None:
            g_window.destroy()
    except Exception:
        traceback.print_exc()
    finally:
        g_window = None
        g_state['pageReady'] = False


def open_custom_window():
    global g_window

    try:
        if g_window is not None:
            close_custom_window()

        read_settings_from_core()
        g_state['pageReady'] = False
        g_state['listeningBind'] = None

        g_window = ModernSettingsWindow()
        g_window.load()
        dlog('Открыто Gameface окно настроек (%s)' % VERSION)
    except Exception as exc:
        g_window = None
        log('Ошибка открытия Gameface окна: %s: %s' %
            (type(exc).__name__, exc), 'err')
        traceback.print_exc()


def switch_to_legacy_settings(permanent=False):
    try:
        from gui.shared import event_dispatcher

        if permanent:
            g_state['useLegacySettings'] = True
            log('Включены старые настройки. Нажмите F10, чтобы вернуть новый интерфейс.', 'warn')

        close_custom_window()
        g_state['bypassHookOnce'] = True
        BigWorld.callback(0.1, event_dispatcher.showSettingsWindow)
    except Exception:
        traceback.print_exc()


def handle_key_event(event):
    try:
        if not event.isKeyDown() or event.isRepeatedEvent():
            return

        # Если окно сейчас ждёт нажатия клавиши для переназначения управления
        listening_target = g_state.get('listeningBind')
        if g_window is not None and listening_target:
            g_state['listeningBind'] = None
            g_state['captureSeq'] = g_state.get('captureSeq', 0) + 1
            if event.key == Keys.KEY_ESCAPE:
                captured_name = 'CANCEL'
            elif event.key in (Keys.KEY_BACKSPACE, Keys.KEY_DELETE):
                captured_name = 'KEY_NONE'
            else:
                captured_name = _key_code_to_name(event.key)

            try:
                g_window.model.send_ack(
                    'keycap-%d' % g_state['captureSeq'],
                    True,
                    {'bindTarget': listening_target, 'capturedKey': captured_name}
                )
            except Exception:
                pass
            return

        now = BigWorld.time()
        if now - g_state.get('lastKeyTime', -10.0) < 0.4:
            return

        if event.key == Keys.KEY_F10:
            g_state['lastKeyTime'] = now
            g_state['useLegacySettings'] = not g_state['useLegacySettings']
            log('Режим: %s' %
                ('стандартные настройки' if g_state['useLegacySettings'] else 'Modern UI'))
        elif event.key == Keys.KEY_F9:
            g_state['lastKeyTime'] = now
            if g_window is not None:
                close_custom_window()
            else:
                open_custom_window()
        elif event.key == Keys.KEY_ESCAPE and g_window is not None:
            g_state['lastKeyTime'] = now
            close_custom_window()
    except Exception:
        traceback.print_exc()


_initialized = [False]


def init():
    if _initialized[0]:
        return
    _initialized[0] = True
    log('Мод запущен (%s). F9 — окно, F10 — смена режима' % VERSION)

    try:
        if InputHandler is not None:
            InputHandler.g_instance.onKeyDown += handle_key_event
    except Exception:
        traceback.print_exc()

    try:
        from gui.Scaleform.daapi.view.lobby.LobbyMenu import LobbyMenu

        if getattr(LobbyMenu, '_modernSettingsHooked', False):
            return

        if not hasattr(LobbyMenu, 'settingsClick'):
            return

        orig_settings_click = LobbyMenu.settingsClick

        def hooked_settings_click(self):
            if g_state.get('useLegacySettings') or g_state.get('bypassHookOnce'):
                g_state['bypassHookOnce'] = False
                orig_settings_click(self)
                return

            try:
                self.destroy()
            except Exception:
                pass

            BigWorld.callback(0.15, open_custom_window)

        LobbyMenu.settingsClick = hooked_settings_click
        LobbyMenu._modernSettingsHooked = True
    except Exception:
        traceback.print_exc()


init()