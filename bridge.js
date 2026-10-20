(function () {
    'use strict';

    if (window.__bridgeLoaded) {
        return;
    }
    window.__bridgeLoaded = true;

    var diag = window.__bridgeDiag = {
        model: false,
        apiRequest: false,
        viewEnv: false,
        helloSent: false,
        stateLen: 0,
        acks: 0,
        error: ''
    };

    var lastAck = '';
    var lastState = '';
    var started = false;
    var dataCallbackRegistered = false;

    function warn(text) {
        diag.error = String(text);
        try { console.warn('[ModernSettings] ' + text); } catch (ignore) {}
    }

    function safeJsonParse(value, fallback) {
        try {
            return JSON.parse(value);
        } catch (e) {
            return fallback;
        }
    }

    function applyStateJson(raw) {
        var uiReady = typeof window.renderContent === 'function';
        if (!raw || (raw === lastState && uiReady && window.__stateAppliedOnce)) {
            return;
        }

        var injected = safeJsonParse(raw, null);
        if (!injected || typeof injected !== 'object') {
            return;
        }

        lastState = raw;
        diag.stateLen = raw.length;
        window.INJECTED = injected;

        var initial = {};
        var current = {};
        var src = injected.settings || {};
        var key;

        for (key in src) {
            if (src.hasOwnProperty(key)) {
                initial[key] = src[key];
                current[key] = src[key];
            }
        }

        window.initialState = initial;
        window.currentState = current;

        if (injected.resolutions && injected.resolutions.length) {
            window.availableResolutions = injected.resolutions.slice();
        }

        if (injected.supported && injected.supported.length) {
            var supportedMap = {};
            for (var i = 0; i < injected.supported.length; i++) {
                supportedMap[injected.supported[i]] = true;
            }
            window.supported = supportedMap;
        } else {
            window.supported = null;
        }

        if (uiReady) {
            window.__stateAppliedOnce = true;
            try {
                if (typeof window.applyThemeFromState === 'function') {
                    window.applyThemeFromState();
                }
                if (typeof window.renderTabs === 'function') {
                    window.renderTabs();
                }
                if (typeof window.renderSidebar === 'function') {
                    window.renderSidebar();
                }
                if (typeof window.renderContent === 'function') {
                    window.renderContent(true);
                }
                if (typeof window.updateFooterState === 'function') {
                    window.updateFooterState();
                }
            } catch (e) {
                warn('state render error: ' + e);
            }
        }
    }

    function processAck(raw) {
        if (!raw || raw === lastAck) {
            return;
        }

        lastAck = raw;
        var ack = safeJsonParse(raw, null);
        if (!ack || !ack.id) {
            return;
        }

        diag.acks++;
        try {
            if (ack.bindTarget && typeof window.__onPythonKeyCaptured === 'function') {
                window.__onPythonKeyCaptured(String(ack.bindTarget), String(ack.capturedKey || ''));
            }
        } catch (e) {}

        try {
            if (typeof window.__ack === 'function') {
                window.__ack(String(ack.id), !!ack.ok);
            }
        } catch (e) {}
    }

    // Отправка через нативный viewEnv.handleViewEvent (GFViewEventProxy -> ViewImpl.createToolTip)
    function sendViaViewEnv(id, cmd, jsonStr) {
        if (typeof window.viewEnv === 'undefined' || typeof window.viewEnv.handleViewEvent !== 'function') {
            return false;
        }
        try {
            window.viewEnv.handleViewEvent({
                __Type: 'GFViewEventProxy',
                type: 1, // ViewEventTypes.tooltip
                contentID: 1,
                decoratorID: 0,
                targetID: 0,
                isMouseEvent: false,
                on: true,
                arguments: [
                    { __Type: 'GFValueProxy', name: 'id', string: String(id) },
                    { __Type: 'GFValueProxy', name: 'cmd', string: String(cmd) },
                    { __Type: 'GFValueProxy', name: 'json', string: String(jsonStr) }
                ]
            });
            return true;
        } catch (e) {
            warn('viewEnv.handleViewEvent: ' + e);
            return false;
        }
    }

    // Отправка через команду ViewModel (все поля строго строковые, без вложенных объектов)
    function sendViaModelCommand(id, cmd, jsonStr) {
        if (!window.model || typeof window.model.apiRequest !== 'function') {
            return false;
        }
        try {
            window.model.apiRequest({
                id: String(id),
                cmd: String(cmd),
                json: String(jsonStr)
            });
            return true;
        } catch (e) {
            warn('model.apiRequest: ' + e);
            return false;
        }
    }

    function dispatchToPython(id, cmd, dataObj) {
        var jsonStr = '{}';
        try {
            jsonStr = JSON.stringify(dataObj || {});
        } catch (e) {
            jsonStr = '{}';
        }

        var sentEnv = sendViaViewEnv(id, cmd, jsonStr);
        var sentCmd = sendViaModelCommand(id, cmd, jsonStr);
        return sentEnv || sentCmd;
    }

    function installPostJSON() {
        window.postJSON = function (url, data, cb) {
            var cmd = String(url || '').replace('/api/', '');
            var sid = window.__sid || (Math.random().toString(36).slice(2, 8));
            var num = Number(window.__n || 0) + 1;
            var id = sid + '-' + num;
            window.__sid = sid;
            window.__n = num;

            if (cb) {
                if (!window.__cbs) {
                    window.__cbs = {};
                }
                window.__cbs[id] = cb;
            }

            var ok = dispatchToPython(id, cmd, data || {});
            if (!ok && window.__cbs && window.__cbs[id]) {
                var f = window.__cbs[id];
                delete window.__cbs[id];
                try { f(false); } catch (ignore) {}
            }
        };
    }

    function registerDataCallback() {
        if (dataCallbackRegistered) {
            return;
        }
        if (typeof window.viewEnv !== 'undefined' && typeof window.viewEnv.addDataChangedCallback === 'function') {
            try {
                window.viewEnv.addDataChangedCallback('model', 0, true);
                dataCallbackRegistered = true;
                diag.viewEnv = true;
            } catch (e) {}
        }
    }

    function poll() {
        if (!window.model) {
            return;
        }
        registerDataCallback();
        applyStateJson(window.model.stateJson || '');
        processAck(window.model.ackJson || '');
    }

    function start() {
        if (started || !window.model) {
            return started;
        }
        started = true;
        diag.model = true;
        diag.apiRequest = typeof window.model.apiRequest === 'function';
        diag.viewEnv = typeof window.viewEnv !== 'undefined';
        diag.error = '';

        registerDataCallback();
        try { poll(); } catch (e) { warn('poll: ' + e); }

        if (window.engine && typeof window.engine.on === 'function') {
            try {
                window.engine.on('viewEnv.onDataChanged', function () {
                    try { poll(); } catch (e) { warn('model update: ' + e); }
                });
            } catch (e) {
                warn('engine.on: ' + e);
            }
        }

        var helloId = 'bridge-hello-' + Math.random().toString(36).slice(2, 8);
        if (dispatchToPython(helloId, 'hello', {})) {
            diag.helloSent = true;
        }
        return true;
    }

    installPostJSON();

    if (window.engine && window.engine.whenReady && typeof window.engine.whenReady.then === 'function') {
        window.engine.whenReady.then(function () {
            registerDataCallback();
            start();
        });
    }

    (function tick() {
        try {
            if (start()) {
                poll();
            }
        } catch (e) {
            warn('tick: ' + e);
        }
        setTimeout(tick, started ? 200 : 300);
    }());
}());
