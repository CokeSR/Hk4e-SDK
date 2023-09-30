(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
    typeof define === 'function' && define.amd ? define(factory) :
    (global = typeof globalThis !== 'undefined' ? globalThis : global || self, global.miHoYoH5log = factory());
})(this, (function () { 'use strict';

    /******************************************************************************
    Copyright (c) Microsoft Corporation.

    Permission to use, copy, modify, and/or distribute this software for any
    purpose with or without fee is hereby granted.

    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
    REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
    AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
    INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
    LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
    OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
    PERFORMANCE OF THIS SOFTWARE.
    ***************************************************************************** */
    /* global Reflect, Promise */

    var extendStatics = function(d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };

    function __extends(d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    }

    var __assign = function() {
        __assign = Object.assign || function __assign(t) {
            for (var s, i = 1, n = arguments.length; i < n; i++) {
                s = arguments[i];
                for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
            }
            return t;
        };
        return __assign.apply(this, arguments);
    };

    function __rest(s, e) {
        var t = {};
        for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
            t[p] = s[p];
        if (s != null && typeof Object.getOwnPropertySymbols === "function")
            for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
                if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                    t[p[i]] = s[p[i]];
            }
        return t;
    }

    function __decorate(decorators, target, key, desc) {
        var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
        if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
        else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
        return c > 3 && r && Object.defineProperty(target, key, r), r;
    }

    function __awaiter(thisArg, _arguments, P, generator) {
        function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
        return new (P || (P = Promise))(function (resolve, reject) {
            function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
            function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
            function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
            step((generator = generator.apply(thisArg, _arguments || [])).next());
        });
    }

    function __generator(thisArg, body) {
        var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
        return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
        function verb(n) { return function (v) { return step([n, v]); }; }
        function step(op) {
            if (f) throw new TypeError("Generator is already executing.");
            while (g && (g = 0, op[0] && (_ = 0)), _) try {
                if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
                if (y = 0, t) op = [op[0] & 2, t.value];
                switch (op[0]) {
                    case 0: case 1: t = op; break;
                    case 4: _.label++; return { value: op[1], done: false };
                    case 5: _.label++; y = op[1]; op = [0]; continue;
                    case 7: op = _.ops.pop(); _.trys.pop(); continue;
                    default:
                        if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                        if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                        if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                        if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                        if (t[2]) _.ops.pop();
                        _.trys.pop(); continue;
                }
                op = body.call(thisArg, _);
            } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
            if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
        }
    }

    var EventEmitter = /** @class */ (function () {
        function EventEmitter() {
            Object.defineProperty(this, "listeners", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: {}
            });
        }
        Object.defineProperty(EventEmitter.prototype, "on", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (eventName, listener) {
                if (!this.listeners[eventName]) {
                    this.listeners[eventName] = [];
                }
                this.listeners[eventName].push(listener);
            }
        });
        Object.defineProperty(EventEmitter.prototype, "off", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (eventName, listener) {
                var eventListeners = this.listeners[eventName];
                if (eventListeners) {
                    var index = eventListeners.indexOf(listener);
                    if (index !== -1) {
                        eventListeners.splice(index, 1);
                    }
                }
            }
        });
        Object.defineProperty(EventEmitter.prototype, "emit", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (eventName) {
                var args = [];
                for (var _i = 1; _i < arguments.length; _i++) {
                    args[_i - 1] = arguments[_i];
                }
                var eventListeners = this.listeners[eventName];
                if (eventListeners) {
                    eventListeners.forEach(function (listener) {
                        listener.apply(void 0, args);
                    });
                }
            }
        });
        Object.defineProperty(EventEmitter.prototype, "clear", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (eventName) {
                delete this.listeners[eventName];
            }
        });
        Object.defineProperty(EventEmitter.prototype, "clearAll", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function () {
                for (var eventName in this.listeners) {
                    delete this.listeners[eventName];
                }
            }
        });
        return EventEmitter;
    }());

    /* eslint-disable @typescript-eslint/ban-ts-comment */
    // @ts-ignore
    // @ts-nocheck
    function debounce$1(func, wait, options) {
        var lastArgs, lastThis, maxWait, result, timerId, lastCallTime;
        var lastInvokeTime = 0;
        var leading = false;
        var maxing = false;
        var trailing = true;
        // Bypass `requestAnimationFrame` by explicitly setting `wait=0`.
        var useRAF = !wait && wait !== 0 && typeof window.requestAnimationFrame === 'function';
        if (typeof func !== 'function') {
            throw new TypeError('Expected a function');
        }
        wait = +wait || 0;
        if (typeof options === 'object') {
            leading = !!options.leading;
            maxing = 'maxWait' in options;
            maxWait = maxing ? Math.max(+options.maxWait || 0, wait) : maxWait;
            trailing = 'trailing' in options ? !!options.trailing : trailing;
        }
        function invokeFunc(time) {
            var args = lastArgs;
            var thisArg = lastThis;
            lastArgs = lastThis = undefined;
            lastInvokeTime = time;
            result = func.apply(thisArg, args);
            return result;
        }
        function startTimer(pendingFunc, wait) {
            if (useRAF) {
                window.cancelAnimationFrame(timerId);
                return window.requestAnimationFrame(pendingFunc);
            }
            return setTimeout(pendingFunc, wait);
        }
        function cancelTimer(id) {
            if (useRAF) {
                return window.cancelAnimationFrame(id);
            }
            clearTimeout(id);
        }
        function leadingEdge(time) {
            // Reset any `maxWait` timer.
            lastInvokeTime = time;
            // Start the timer for the trailing edge.
            timerId = startTimer(timerExpired, wait);
            // Invoke the leading edge.
            return leading ? invokeFunc(time) : result;
        }
        function remainingWait(time) {
            var timeSinceLastCall = time - lastCallTime;
            var timeSinceLastInvoke = time - lastInvokeTime;
            var timeWaiting = wait - timeSinceLastCall;
            return maxing
                ? Math.min(timeWaiting, maxWait - timeSinceLastInvoke)
                : timeWaiting;
        }
        function shouldInvoke(time) {
            var timeSinceLastCall = time - lastCallTime;
            var timeSinceLastInvoke = time - lastInvokeTime;
            // Either this is the first call, activity has stopped and we're at the
            // trailing edge, the system time has gone backwards and we're treating
            // it as the trailing edge, or we've hit the `maxWait` limit.
            return (lastCallTime === undefined ||
                timeSinceLastCall >= wait ||
                timeSinceLastCall < 0 ||
                (maxing && timeSinceLastInvoke >= maxWait));
        }
        function timerExpired() {
            var time = Date.now();
            if (shouldInvoke(time)) {
                return trailingEdge(time);
            }
            // Restart the timer.
            timerId = startTimer(timerExpired, remainingWait(time));
        }
        function trailingEdge(time) {
            timerId = undefined;
            // Only invoke if we have `lastArgs` which means `func` has been
            // debounced at least once.
            if (trailing && lastArgs) {
                return invokeFunc(time);
            }
            lastArgs = lastThis = undefined;
            return result;
        }
        function cancel() {
            if (timerId !== undefined) {
                cancelTimer(timerId);
            }
            lastInvokeTime = 0;
            lastArgs = lastCallTime = lastThis = timerId = undefined;
        }
        function flush() {
            return timerId === undefined ? result : trailingEdge(Date.now());
        }
        function pending() {
            return timerId !== undefined;
        }
        function debounced() {
            var args = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                args[_i] = arguments[_i];
            }
            var time = Date.now();
            var isInvoking = shouldInvoke(time);
            lastArgs = args;
            // eslint-disable-next-line @typescript-eslint/no-this-alias
            lastThis = this;
            lastCallTime = time;
            if (isInvoking) {
                if (timerId === undefined) {
                    return leadingEdge(lastCallTime);
                }
                if (maxing) {
                    // Handle invocations in a tight loop.
                    timerId = startTimer(timerExpired, wait);
                    return invokeFunc(lastCallTime);
                }
            }
            if (timerId === undefined) {
                timerId = startTimer(timerExpired, wait);
            }
            return result;
        }
        debounced.cancel = cancel;
        debounced.flush = flush;
        debounced.pending = pending;
        return debounced;
    }

    function debounce(wait, maxWait) {
        return function (target, propertyKey, descriptor) {
            var originalMethod = descriptor.value;
            descriptor.value = debounce$1(originalMethod, wait, { maxWait: maxWait });
            return descriptor;
        };
    }

    var LocalStorageStore = /** @class */ (function () {
        function LocalStorageStore(storageKeySuffix) {
            var _this = this;
            Object.defineProperty(this, "storageKey", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: void 0
            });
            Object.defineProperty(this, "innerStore", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: void 0
            });
            this.storageKey = "MIHOYO_H5LOG_".concat(storageKeySuffix);
            var localData = this.getLocalData(localStorage.getItem(this.storageKey));
            this.innerStore = localData ? localData : [];
            this.updateLocalData();
            window.addEventListener('unload', function () {
                _this.updateLocalDataSync();
            });
        }
        Object.defineProperty(LocalStorageStore.prototype, "getLocalData", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (data) {
                try {
                    if (!data)
                        return false;
                    var parsedData = JSON.parse(data);
                    if (!Array.isArray(parsedData))
                        return false;
                    return parsedData.filter(function (v) { return v.app_name; });
                }
                catch (error) {
                    return false;
                }
            }
        });
        Object.defineProperty(LocalStorageStore.prototype, "updateLocalData", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function () {
                try {
                    var data = this.innerStore;
                    var value = JSON.stringify(data);
                    localStorage.setItem(this.storageKey, value);
                }
                catch (error) {
                    if (error instanceof DOMException &&
                        (error.code === 22 ||
                            error.code === 1014 ||
                            error.name === 'QuotaExceededError' ||
                            error.name === 'NS_ERROR_DOM_QUOTA_REACHED')) {
                        // 澶勭悊 localStorage 瀹归噺涓嶈冻鐨勯敊璇�
                        this.innerStore.splice(0, this.innerStore.length / 2);
                    }
                }
            }
        });
        Object.defineProperty(LocalStorageStore.prototype, "updateLocalDataSync", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function () {
                try {
                    var data = this.innerStore;
                    var value = JSON.stringify(data);
                    localStorage.setItem(this.storageKey, value);
                }
                catch (error) {
                    // noop
                }
            }
        });
        Object.defineProperty(LocalStorageStore.prototype, "push", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (data) {
                this.innerStore.push(data);
                this.updateLocalData();
            }
        });
        Object.defineProperty(LocalStorageStore.prototype, "length", {
            get: function () {
                return this.innerStore.length;
            },
            enumerable: false,
            configurable: true
        });
        Object.defineProperty(LocalStorageStore.prototype, "splice", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (start, deleteCount) {
                var data = this.innerStore.splice(start, deleteCount);
                this.updateLocalData();
                return data;
            }
        });
        Object.defineProperty(LocalStorageStore.prototype, "getFirst", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function () {
                return this.innerStore[0];
            }
        });
        Object.defineProperty(LocalStorageStore.prototype, "getLast", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function () {
                if (this.innerStore.length === 0)
                    return undefined;
                return this.innerStore[this.innerStore.length - 1];
            }
        });
        __decorate([
            debounce(200, 1000)
        ], LocalStorageStore.prototype, "updateLocalData", null);
        return LocalStorageStore;
    }());

    var MemoryStore = /** @class */ (function () {
        function MemoryStore() {
            Object.defineProperty(this, "innerStore", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: void 0
            });
            this.innerStore = [];
        }
        Object.defineProperty(MemoryStore.prototype, "push", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (data) {
                this.innerStore.push(data);
            }
        });
        Object.defineProperty(MemoryStore.prototype, "length", {
            get: function () {
                return this.innerStore.length;
            },
            enumerable: false,
            configurable: true
        });
        Object.defineProperty(MemoryStore.prototype, "splice", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (start, deleteCount) {
                return this.innerStore.splice(start, deleteCount);
            }
        });
        Object.defineProperty(MemoryStore.prototype, "getFirst", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function () {
                return this.innerStore[0];
            }
        });
        Object.defineProperty(MemoryStore.prototype, "getLast", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function () {
                if (this.innerStore.length === 0)
                    return undefined;
                return this.innerStore[this.innerStore.length - 1];
            }
        });
        return MemoryStore;
    }());

    var IStorageType;
    (function (IStorageType) {
        IStorageType["Memory"] = "memory";
        IStorageType["Local"] = "local";
    })(IStorageType || (IStorageType = {}));

    var H5logCollector = /** @class */ (function (_super) {
        __extends(H5logCollector, _super);
        function H5logCollector(collectOptions) {
            var _a, _b, _c, _d;
            var _this = _super.call(this) || this;
            Object.defineProperty(_this, "collectOptions", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: void 0
            });
            Object.defineProperty(_this, "store", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: void 0
            });
            Object.defineProperty(_this, "prevBatchEventTimes", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: void 0
            });
            Object.defineProperty(_this, "timer", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: void 0
            });
            if (collectOptions) {
                var DEFAULT_COLLECTOR_OPTIONS = H5logCollector.DEFAULT_COLLECTOR_OPTIONS;
                var batchSize = (_a = collectOptions.batchSize, _a === void 0 ? DEFAULT_COLLECTOR_OPTIONS.batchSize : _a), batchInterval = (_b = collectOptions.batchInterval, _b === void 0 ? DEFAULT_COLLECTOR_OPTIONS.batchInterval : _b);
                var highPriorityList = (_c = collectOptions.highPriorityList, _c === void 0 ? DEFAULT_COLLECTOR_OPTIONS.highPriorityList : _c), storageType = (_d = collectOptions.storageType, _d === void 0 ? DEFAULT_COLLECTOR_OPTIONS.storageType : _d);
                if (typeof batchSize === 'number' && (batchSize > 20 || batchSize <= 0)) {
                    console.warn("[h5log]: The parameter 'batchSize' is invalid.");
                    batchSize = DEFAULT_COLLECTOR_OPTIONS.batchSize;
                }
                if (typeof batchInterval === 'number' && batchInterval <= 0) {
                    console.warn("[h5log]: The parameter 'batchInterval' is invalid.\"");
                    batchInterval = DEFAULT_COLLECTOR_OPTIONS.batchInterval;
                }
                if (storageType === IStorageType.Local) {
                    var storageKeySuffix = collectOptions.storageKeySuffix;
                    _this.store = new LocalStorageStore(storageKeySuffix);
                    _this.collectOptions = {
                        batchSize: batchSize,
                        highPriorityList: highPriorityList,
                        storageType: storageType,
                        batchInterval: batchInterval,
                        storageKeySuffix: storageKeySuffix,
                    };
                }
                else {
                    _this.store = new MemoryStore();
                    _this.collectOptions = {
                        batchSize: batchSize,
                        highPriorityList: highPriorityList,
                        storageType: storageType,
                        batchInterval: batchInterval,
                    };
                }
            }
            else {
                _this.collectOptions = H5logCollector.DEFAULT_COLLECTOR_OPTIONS;
                _this.store = new MemoryStore();
            }
            _this.prevBatchEventTimes = Date.now();
            _this.initialInterval();
            return _this;
        }
        Object.defineProperty(H5logCollector.prototype, "first", {
            get: function () {
                return this.store.getFirst();
            },
            enumerable: false,
            configurable: true
        });
        Object.defineProperty(H5logCollector.prototype, "last", {
            get: function () {
                return this.store.getLast();
            },
            enumerable: false,
            configurable: true
        });
        Object.defineProperty(H5logCollector.prototype, "list", {
            get: function () {
                return this.store.innerStore;
            },
            enumerable: false,
            configurable: true
        });
        Object.defineProperty(H5logCollector.prototype, "collect", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (data) {
                this.store.push(data);
                this.shouldSend();
            }
        });
        Object.defineProperty(H5logCollector.prototype, "disableInterval", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function () {
                if (this.timer) {
                    clearInterval(this.timer);
                }
            }
        });
        Object.defineProperty(H5logCollector.prototype, "resetInterval", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (rate) {
                this.disableInterval();
                var batchInterval = this.collectOptions.batchInterval;
                this.collectOptions.batchInterval = batchInterval * rate;
                this.initialInterval();
            }
        });
        Object.defineProperty(H5logCollector.prototype, "initialInterval", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function () {
                var _this = this;
                var batchInterval = this.collectOptions.batchInterval;
                this.timer = setInterval(function () {
                    _this.shouldSend(true);
                }, batchInterval);
            }
        });
        Object.defineProperty(H5logCollector.prototype, "emitBatch", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function () {
                var _a;
                var batchSize = (_a = this.collectOptions, _a.batchSize), batchInterval = _a.batchInterval;
                var dis = Date.now() - this.prevBatchEventTimes;
                if (dis < batchInterval) {
                    return;
                }
                var data = this.store.splice(0, batchSize);
                this.prevBatchEventTimes = Date.now();
                this.emit('flush', data);
            }
        });
        Object.defineProperty(H5logCollector.prototype, "shouldSend", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (checkStoreSize) {
                var _a;
                if (checkStoreSize === void 0) { checkStoreSize = false; }
                var highPriorityList = (_a = this.collectOptions, _a.highPriorityList), batchSize = _a.batchSize;
                if (this.last && highPriorityList.indexOf(this.last.level) > -1) {
                    this.emitBatch();
                }
                if (this.store.length >= batchSize) {
                    this.emitBatch();
                }
                if (checkStoreSize && this.store.length > 0) {
                    this.emitBatch();
                }
            }
        });
        Object.defineProperty(H5logCollector, "DEFAULT_COLLECTOR_OPTIONS", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: {
                highPriorityList: ['error'],
                storageType: IStorageType.Memory,
                batchSize: 20,
                batchInterval: 3 * 1000,
            }
        });
        return H5logCollector;
    }(EventEmitter));

    var CNBatchUrl;
    (function (CNBatchUrl) {
        CNBatchUrl["development"] = "https://devapi-takumi.mihoyo.com/common/h5log/log/batch?topic=";
        CNBatchUrl["test"] = "https://devapi-takumi.mihoyo.com/common/h5log/log/batch?topic=";
        CNBatchUrl["prerelease"] = "https://api-takumi.mihoyo.com/common/h5log/log/batch?topic=";
        CNBatchUrl["beta"] = "https://minor-api.mihoyo.com/common/h5log/log/batch?topic=";
        CNBatchUrl["sandbox"] = "https://devapi-takumi.mihoyo.com/common/h5log/log/batch?topic=";
        CNBatchUrl["production"] = "https://minor-api.mihoyo.com/common/h5log/log/batch?topic=";
    })(CNBatchUrl || (CNBatchUrl = {}));
    var OSBatchUrl;
    (function (OSBatchUrl) {
        OSBatchUrl["development"] = "https://devapi-os-takumi.hoyoverse.com/common/h5log/log/batch?topic=";
        OSBatchUrl["test"] = "https://devapi-os-takumi.hoyoverse.com/common/h5log/log/batch?topic=";
        OSBatchUrl["prerelease"] = "https://api-os-takumi.hoyoverse.com/common/h5log/log/batch?topic=";
        OSBatchUrl["beta"] = "https://minor-api-os.hoyoverse.com/common/h5log/log/batch?topic=";
        OSBatchUrl["sandbox"] = "https://devapi-os-takumi.hoyoverse.com/common/h5log/log/batch?topic=";
        OSBatchUrl["production"] = "https://minor-api-os.hoyoverse.com/common/h5log/log/batch?topic=";
    })(OSBatchUrl || (OSBatchUrl = {}));

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    //@ts-nocheck
    var Rc4B64Class = /** @class */ (function () {
        function Rc4B64Class() {
            this.keyStr =
                'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
        }
        Object.defineProperty(Rc4B64Class.prototype, "Encrypt", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (strTexto, strClave) {
                return this.encode64(this._RC4(strTexto, strClave));
            }
        });
        Object.defineProperty(Rc4B64Class.prototype, "Decrypt", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (strTexto, strClave) {
                return this._RC4(this.decode64(strTexto), strClave);
            }
        });
        Object.defineProperty(Rc4B64Class.prototype, "InicializarRC4", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (strLlave) {
                var _a;
                var sbox = new Array(256).fill(0);
                var key = new Array(256).fill(0);
                for (var a = 0; a < 256; a++) {
                    key[a] = strLlave.charCodeAt(a % strLlave.length);
                    sbox[a] = a;
                }
                var j = 0;
                for (var i = 0; i < 256; i++) {
                    j = (j + sbox[i] + key[i]) % 256;
                    _a = [sbox[j], sbox[i]], sbox[i] = _a[0], sbox[j] = _a[1];
                }
                return sbox;
            }
        });
        Object.defineProperty(Rc4B64Class.prototype, "_RC4", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (strTexto, strClave) {
                var _a;
                var sbox = this.InicializarRC4(strClave);
                var i = 0, j = 0;
                var cipher = '';
                var cipherby, k;
                for (var a = 0; a < strTexto.length; a++) {
                    i = (i + 1) % 256;
                    j = (j + sbox[i]) % 256;
                    _a = [sbox[j], sbox[i]], sbox[i] = _a[0], sbox[j] = _a[1];
                    k = sbox[(sbox[i] + sbox[j]) % 256];
                    cipherby = strTexto.charCodeAt(a) ^ k;
                    cipher += String.fromCharCode(cipherby);
                }
                return cipher;
            }
        });
        Object.defineProperty(Rc4B64Class.prototype, "encode64", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (input) {
                var output = '';
                var chr1, chr2, chr3 = '';
                var enc1, enc2, enc3, enc4 = '';
                var i = 0;
                do {
                    chr1 = input.charCodeAt(i++);
                    chr2 = input.charCodeAt(i++);
                    chr3 = input.charCodeAt(i++);
                    enc1 = chr1 >> 2;
                    enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
                    enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
                    enc4 = chr3 & 63;
                    if (isNaN(chr2)) {
                        enc3 = enc4 = 64;
                    }
                    else if (isNaN(chr3)) {
                        enc4 = 64;
                    }
                    output +=
                        this.keyStr.charAt(enc1) +
                            this.keyStr.charAt(enc2) +
                            this.keyStr.charAt(enc3) +
                            this.keyStr.charAt(enc4);
                    chr1 = chr2 = chr3 = '';
                    enc1 = enc2 = enc3 = enc4 = '';
                } while (i < input.length);
                return output;
            }
        });
        Object.defineProperty(Rc4B64Class.prototype, "decode64", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (input) {
                var output = '';
                var chr1, chr2, chr3 = '';
                var enc1, enc2, enc3, enc4 = '';
                var i = 0;
                input = input.replace(/[^A-Za-z0-9+/=]/g, '');
                do {
                    enc1 = this.keyStr.indexOf(input.charAt(i++));
                    enc2 = this.keyStr.indexOf(input.charAt(i++));
                    enc3 = this.keyStr.indexOf(input.charAt(i++));
                    enc4 = this.keyStr.indexOf(input.charAt(i++));
                    chr1 = (enc1 << 2) | (enc2 >> 4);
                    chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
                    chr3 = ((enc3 & 3) << 6) | enc4;
                    output += String.fromCharCode(chr1);
                    if (enc3 !== 64) {
                        output += String.fromCharCode(chr2);
                    }
                    if (enc4 !== 64) {
                        output += String.fromCharCode(chr3);
                    }
                    chr1 = chr2 = chr3 = '';
                    enc1 = enc2 = enc3 = enc4 = '';
                } while (i < input.length);
                return output;
            }
        });
        return Rc4B64Class;
    }());
    var SECRET_KEY = 'F#ju0q8I9HbmH8PMpJzzBee&p0b5h@Yb';
    function rc4EncryptWithBase64(key, plaintext) {
        if (plaintext === void 0) { plaintext = SECRET_KEY; }
        var rc4 = new Rc4B64Class();
        return rc4.Encrypt(key, plaintext);
    }

    function request(options) {
        var xhr = new XMLHttpRequest();
        var method = options.method || 'GET';
        var url = options.url;
        var async = options.async || true;
        var timeout = options.timeout || 0;
        xhr.open(method, url, async);
        xhr.timeout = timeout;
        if (options.headers) {
            for (var key in options.headers) {
                xhr.setRequestHeader(key, options.headers[key]);
            }
        }
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(options.data);
        return new Promise(function (resolve, reject) {
            xhr.onload = function () {
                try {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        var response = JSON.parse(xhr.responseText);
                        if (response.retcode === 0) {
                            resolve(response);
                        }
                        else {
                            reject(xhr);
                        }
                    }
                    else {
                        reject(xhr);
                    }
                }
                catch (error) {
                    reject(xhr);
                }
            };
            xhr.onerror = function () {
                reject(xhr);
            };
            xhr.ontimeout = function () {
                reject(__assign(__assign({}, xhr), { isTimeout: true }));
            };
        });
    }

    var BatchUrl;
    (function (BatchUrl) {
        BatchUrl["development"] = "https://devapi-takumi.mihoyo.com/common/h5log/log/batch?topic=";
        BatchUrl["test"] = "https://devapi-takumi.mihoyo.com/common/h5log/log/batch?topic=";
        BatchUrl["prerelease"] = "https://api-takumi.mihoyo.com/common/h5log/log/batch?topic=";
        BatchUrl["beta"] = "https://minor-api.mihoyo.com/common/h5log/log/batch?topic=";
        BatchUrl["sandbox"] = "https://devapi-takumi.mihoyo.com/common/h5log/log/batch?topic=";
        BatchUrl["production"] = "https://minor-api.mihoyo.com/common/h5log/log/batch?topic=";
    })(BatchUrl || (BatchUrl = {}));
    var SenderEnv;
    (function (SenderEnv) {
        SenderEnv["Development"] = "development";
        SenderEnv["Test"] = "test";
        SenderEnv["Prerelease"] = "prerelease";
        SenderEnv["Beta"] = "beta";
        SenderEnv["Sandbox"] = "sandbox";
        SenderEnv["Production"] = "production";
    })(SenderEnv || (SenderEnv = {}));
    var Region;
    (function (Region) {
        Region["CN"] = "cn";
        Region["OS"] = "os";
    })(Region || (Region = {}));

    var H5logSender = /** @class */ (function (_super) {
        __extends(H5logSender, _super);
        function H5logSender(opts) {
            var _this = _super.call(this) || this;
            Object.defineProperty(_this, "sendOptions", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: void 0
            });
            _this.sendOptions = {
                topic: opts.topic,
                env: opts.env || H5logSender.DEFAULT_SENDER_OPTIONS.env,
                region: opts.region || H5logSender.DEFAULT_SENDER_OPTIONS.region,
            };
            return _this;
        }
        Object.defineProperty(H5logSender.prototype, "send", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (data, retryTimes) {
                if (retryTimes === void 0) { retryTimes = 0; }
                return __awaiter(this, void 0, void 0, function () {
                    var env, topic, region, baseUrl, url, error_1;
                    var _a;
                    return __generator(this, function (_b) {
                        switch (_b.label) {
                            case 0:
                                env = (_a = this.sendOptions, _a.env), topic = _a.topic, region = _a.region;
                                baseUrl = region === Region.CN ? CNBatchUrl : OSBatchUrl;
                                url = "".concat(baseUrl[env]).concat(topic);
                                _b.label = 1;
                            case 1:
                                _b.trys.push([1, 3, , 4]);
                                return [4 /*yield*/, request({
                                        url: url,
                                        method: 'POST',
                                        timeout: 5000,
                                        data: JSON.stringify({
                                            data: rc4EncryptWithBase64(JSON.stringify({ data: data })),
                                        }),
                                    })];
                            case 2:
                                _b.sent();
                                return [3 /*break*/, 4];
                            case 3:
                                error_1 = _b.sent();
                                if (error_1 instanceof XMLHttpRequest) {
                                    if (error_1.status > 400) {
                                        this.emit('serverError');
                                    }
                                    else if (error_1.isTimeout && retryTimes === 0) {
                                        this.send(data, retryTimes + 1);
                                    }
                                }
                                return [3 /*break*/, 4];
                            case 4: return [2 /*return*/];
                        }
                    });
                });
            }
        });
        Object.defineProperty(H5logSender, "SECRET_KEY", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: SECRET_KEY
        });
        Object.defineProperty(H5logSender, "DEFAULT_SENDER_OPTIONS", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: {
                env: SenderEnv.Production,
                region: Region.CN,
            }
        });
        return H5logSender;
    }(EventEmitter));

    var Level;
    (function (Level) {
        Level["Error"] = "error";
        Level["Warn"] = "warn";
        Level["Info"] = "info";
    })(Level || (Level = {}));
    var ErrorCode;
    (function (ErrorCode) {
        ErrorCode["Error"] = "-1";
    })(ErrorCode || (ErrorCode = {}));
    var Code;
    (function (Code) {
        Code["Warn"] = "0";
        Code["Info"] = "0";
    })(Code || (Code = {}));

    var H5log = /** @class */ (function () {
        function H5log(collector, sender, options) {
            var _this = this;
            var _a, _b;
            Object.defineProperty(this, "collector", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: void 0
            });
            Object.defineProperty(this, "sender", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: void 0
            });
            Object.defineProperty(this, "options", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: void 0
            });
            Object.defineProperty(this, "commonInfo", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: void 0
            });
            Object.defineProperty(this, "serverErrorCount", {
                enumerable: true,
                configurable: true,
                writable: true,
                value: void 0
            });
            this.collector = collector;
            this.sender = sender;
            this.commonInfo = null;
            this.options = {
                enable: (_a = options === null || options === void 0 ? void 0 : options.enable) !== null && _a !== void 0 ? _a : true,
                debug: (_b = options === null || options === void 0 ? void 0 : options.debug) !== null && _b !== void 0 ? _b : false,
            };
            this.serverErrorCount = 0;
            this.collector.on('flush', this.sender.send.bind(this.sender));
            this.sender.on('serverError', function () {
                _this.serverErrorCount += 1;
                if (_this.serverErrorCount >= H5log.MAX_SERVER_ERROR) {
                    _this.options.enable = false;
                    _this.collector.disableInterval();
                }
                else if (_this.serverErrorCount > 1) {
                    _this.collector.resetInterval(_this.serverErrorCount);
                }
            });
        }
        Object.defineProperty(H5log, "create", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (options) {
                var _a, _b, _c;
                if (![
                    'development',
                    'test',
                    'prerelease',
                    'beta',
                    'sandbox',
                    'production',
                ].includes(options.env)) {
                    console.error("[h5log]: parameter env: ".concat(options.env, " is not allowed"));
                    options.env = 'production';
                }
                var env = options.env, topic = options.topic, region = (_a = options.region, _a === void 0 ? Region.CN : _a), enable = (_b = options.enable, _b === void 0 ? true : _b), debug = (_c = options.debug, _c === void 0 ? false : _c), collectorOptions = __rest(options, ["env", "topic", "region", "enable", "debug"]);
                var storageType = collectorOptions.storageType;
                if (!topic) {
                    console.error("[h5log]: parameter topic is required");
                }
                var collector = storageType === IStorageType.Local
                    ? new H5logCollector(__assign(__assign({}, collectorOptions), { storageKeySuffix: collectorOptions.storageKeySuffix || "".concat(env, "_").concat(topic, "_").concat(region) }))
                    : new H5logCollector(collectorOptions);
                var sender = new H5logSender({ env: env, topic: topic, region: region });
                return new H5log(collector, sender, {
                    enable: enable,
                    debug: debug,
                });
            }
        });
        Object.defineProperty(H5log.prototype, "setCommonInfo", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (commonInfo) {
                this.commonInfo = commonInfo;
            }
        });
        Object.defineProperty(H5log.prototype, "error", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (msg, code, additionalData) {
                if (code === void 0) { code = ErrorCode.Error; }
                this.log(msg, code, 'error', additionalData);
            }
        });
        Object.defineProperty(H5log.prototype, "warn", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (msg, additionalData) {
                this.log(msg, Code.Warn, 'warn', additionalData);
            }
        });
        Object.defineProperty(H5log.prototype, "info", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (msg, additionalData) {
                this.log(msg, Code.Info, 'info', additionalData);
            }
        });
        Object.defineProperty(H5log.prototype, "log", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (msg, code, level, additionalData) {
                var _a;
                var enable = (_a = this.options, _a.enable), debug = _a.debug;
                if (!enable) {
                    return;
                }
                if (/[\u4e00-\u9fa5]/.test(msg)) {
                    msg = msg.replace(/[\u4e00-\u9fa5]/g, '');
                }
                var payload = __assign(__assign({ msg: msg, code: code, level: level, timestamp: "".concat(Date.now()), '@timestamp': "".concat(new Date().toISOString()) }, this.commonInfo), additionalData);
                if (debug && typeof console[level] === 'function') {
                    console[level]("[h5log]: ".concat(msg), payload);
                }
                if (!payload.app_name) {
                    console.warn("[h5log]: Invalid data, the app_name parameter is undefined.");
                    return;
                }
                this.collector.collect(this.normalizePayload(payload));
            }
        });
        Object.defineProperty(H5log.prototype, "normalizePayload", {
            enumerable: false,
            configurable: true,
            writable: true,
            value: function (payload) {
                if (!payload)
                    return payload;
                var keys = Object.keys(payload);
                return keys.reduce(function (cur, key) {
                    var data = payload[key];
                    if (typeof data === 'string' && /[\u4e00-\u9fa5]/.test(data)) {
                        cur[key] = data.replace(/[\u4e00-\u9fa5]/g, '*');
                    }
                    else if (typeof data === 'object') {
                        try {
                            cur[key] = JSON.stringify(data).replace(/[\u4e00-\u9fa5]/g, '*');
                        }
                        catch (error) {
                            cur[key] = "[h5log]: data dropped, stringify err";
                        }
                    }
                    else {
                        cur[key] = data;
                    }
                    return cur;
                }, {});
            }
        });
        Object.defineProperty(H5log.prototype, "list", {
            get: function () {
                return this.collector.list;
            },
            enumerable: false,
            configurable: true
        });
        Object.defineProperty(H5log, "MAX_SERVER_ERROR", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: 5
        });
        Object.defineProperty(H5log, "H5logCollector", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: H5logCollector
        });
        Object.defineProperty(H5log, "H5logSender", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: H5logSender
        });
        Object.defineProperty(H5log, "H5logSenderEnv", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: SenderEnv
        });
        Object.defineProperty(H5log, "H5logSenderRegion", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: Region
        });
        return H5log;
    }());

    return H5log;

}));