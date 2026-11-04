/* Ultimate-skill reskin overlay.
 *
 * The 86-player roster got new ultimate clips rendered as transparent frame
 * sequences (see tools/street_ultimate_mat.py). Egret cannot hold a 720x720
 * x N RGBA sequence as DragonBones atlases, so the new art is played as a
 * streamed bitmap sequence on top of the battle layer:
 *
 *   - DBEffect.trigger is wrapped; when the effect is one of a hero's unique
 *     ultimate layers the original armature is hidden (visible = false) and one
 *     overlay is started for that cast,
 *   - the overlay keeps the ORIGINAL container's frame count and fps (retimed
 *     at build time), and multiplies by the effect's own timeScale, so the
 *     duration and the skill clock stay identical to the original,
 *   - frames are WebP resources fetched a few ahead of the playhead and freed
 *     behind it, so a 96-frame clip never sits fully in memory.
 *
 * Game logic, damage, events and the skill clock are untouched: only pixels are
 * replaced, and every failure falls back to the original effect.
 */
(function (global) {
  'use strict';

  var DATA = global.StreetUltimateData || { heroes: {} };
  var HEROES = DATA.heroes || {};
  var BY_KEY = {};
  var OWNERS = {};
  (function () {
    for (var id in HEROES) {
      if (!Object.prototype.hasOwnProperty.call(HEROES, id)) continue;
      var keys = HEROES[id].keys || [];
      for (var i = 0; i < keys.length; i++) BY_KEY[keys[i]] = Number(id);
      var all = HEROES[id].allKeys || keys;
      for (var j = 0; j < all.length; j++) {
        if (!OWNERS[all[j]]) OWNERS[all[j]] = [];
        OWNERS[all[j]].push(Number(id));
      }
    }
  })();

  var PREFETCH = 10;
  var KEEP_BACK = 6;
  var START_FRAMES = 4;
  var CAST_WINDOW_MS = 1600;
  var IMAGE = (global.RES && RES.ResourceItem && RES.ResourceItem.TYPE_IMAGE) || 'image';

  var state = {
    installed: false,
    triggers: 0,
    matched: 0,
    hidden: 0,
    overlays: 0,
    frames: 0,
    errors: [],
    active: [],
    finished: [],
    lastCast: {},
    pending: null,
    refs: {}
  };

  function error(where, err) {
    if (state.errors.length < 20) state.errors.push(where + ': ' + String((err && err.message) || err));
  }

  function baseName(name) {
    var s = String(name || '');
    if (s.length > 3 && s.slice(-3) === '_ez') s = s.slice(0, -3);
    if (s.indexOf('street_') === 0) s = s.slice(7);
    return s;
  }

  function url(base, file) {
    return '/' + base + '/' + file;
  }

  function acquire(name) {
    state.refs[name] = (state.refs[name] || 0) + 1;
  }

  function release(name) {
    state.refs[name] = Math.max(0, (state.refs[name] || 1) - 1);
    if (state.refs[name] > 0) return;
    try { RES.destroyRes(name, true); } catch (e) { /* already gone */ }
  }

  function Overlay(heroId, hero, effect) {
    this.heroId = heroId;
    this.hero = hero;
    this.effect = effect;
    this.step = 1000 / Math.max(1, hero.fps * (effect.timeScale || 1));
    this.total = hero.frames;
    this.frame = -1;
    this.cache = {};
    this.pending = {};
    this.dead = false;
    this.startedAt = 0;
    this.lastTick = 0;
    this.presented = 0;
    this.container = new egret.Sprite();
    this.container.name = 'street_ultimate_' + heroId;
    this.container.touchEnabled = false;
    this.bitmap = new egret.Bitmap();
    this.bitmap.touchEnabled = false;
    this.container.addChild(this.bitmap);
    var target = effect.parent || global.egret && egret.MainContext.instance.stage;
    if (!target) return;
    var cx = Math.max(0, target.width || 0) / 2;
    var cy = Math.max(0, target.height || 0) / 2;
    if (!cx || !cy) {
      var stage = egret.MainContext.instance.stage;
      cx = stage.stageWidth / 2;
      cy = stage.stageHeight / 2;
    }
    this.container.x = cx;
    this.container.y = cy;
    this.container.zIndex = (effect.zIndex || 0) + 1;
    target.addChild(this.container);
    if (typeof target.sortChildren === 'function') {
      try { target.sortChildren(); } catch (e) { /* optional */ }
    }
    this.center = { x: hero.canvas / 2, y: hero.canvas / 2 };
    this.start();
  }

  Overlay.prototype.start = function () {
    var self = this;
    this.waitFrom = egret.getTimer();
    for (var i = 0; i < START_FRAMES * 2; i++) this.ensure(i);
    this.timer = egret.setInterval(function () { self.tick(); }, this, 16);
  };

  Overlay.prototype.ensure = function (idx, immediate) {
    if (idx < 0 || idx >= this.total) return;
    if (this.cache[idx] || this.pending[idx]) return;
    var name = url(this.hero.dir, this.hero.files[idx]);
    this.pending[idx] = true;
    acquire(name);
    var self = this;
    try {
      RES.getResByUrl(name, function (texture) {
        self.pending[idx] = false;
        if (self.dead) { release(name); return; }
        if (!texture) { release(name); return; }
        self.cache[idx] = texture;
      }, this, IMAGE);
    } catch (e) {
      this.pending[idx] = false;
      release(name);
      error('load', e);
    }
  };

  Overlay.prototype.tick = function () {
    if (this.dead) return;
    // Keep the original art hidden for as long as the overlay runs.
    if (this.effect && this.effect.visible) {
      this.effect.visible = false;
      state.hidden++;
    }
    if (this.startedAt && this.container && !this.container.stage) { this.finish(); return; }
    var now = egret.getTimer();
    if (!this.startedAt) {
      // Wait until the opening frames are decoded so the clip does not start
      // with a stall; bail out of the wait after 700 ms.
      this.ensure(0);
      var ready = 0;
      for (var k = 0; k < START_FRAMES; k++) if (this.cache[k]) ready++;
      if (ready < START_FRAMES && now - this.waitFrom < 700) return;
      this.startedAt = now;
      this.lastTick = now;
      this.held = 0;
      return;
    }
    var elapsed = now - this.startedAt - this.held;
    if (elapsed < 0) elapsed = 0;
    var want = Math.floor(elapsed / this.step);
    if (want >= this.total) { this.finish(); return; }
    if (want <= this.frame) {
      this.lastTick = now;
      this.prefetch(this.frame + 1, this.frame + PREFETCH);
      return;
    }
    var tex = this.cache[want];
    if (!tex) {
      // Hold the clock while the frame decodes: every frame must be shown, so a
      // slow decode stretches the clip slightly instead of dropping frames.
      var dt = now - this.lastTick;
      this.held += dt;
      this.stallFor = (this.stallFor || 0) + dt;
      this.lastTick = now;
      this.ensure(want);
      if (this.stallFor > 600) { this.held -= this.step; this.stallFor = 0; }
      return;
    }
    this.stallFor = 0;
    this.lastTick = now;
    if (want > this.frame + 1) {
      this.skipped = (this.skipped || 0) + (want - this.frame - 1);
      if (!this.skipAt) this.skipAt = [];
      if (this.skipAt.length < 12) this.skipAt.push(want);
    }
    this.frame = want;
    this.bitmap.texture = tex;
    this.presented++;
    var box = this.hero.boxes[want];
    this.bitmap.x = box[0] - this.center.x;
    this.bitmap.y = box[1] - this.center.y;
    state.frames++;
    this.prefetch(this.frame + 1, this.frame + PREFETCH);
    for (var j = 0; j < this.frame - KEEP_BACK; j++) {
      if (this.cache[j]) {
        var name = url(this.hero.dir, this.hero.files[j]);
        if (this.bitmap.texture === this.cache[j]) this.bitmap.texture = null;
        delete this.cache[j];
        release(name);
      }
    }
  };

  Overlay.prototype.prefetch = function (from, to) {
    for (var i = from; i <= to; i++) this.ensure(i);
  };

  Overlay.prototype.finish = function () {
    if (this.dead) return;
    this.dead = true;
    if (this.timer) { egret.clearInterval(this.timer); this.timer = 0; }
    state.finished.push({ heroId: this.heroId, presented: this.presented, total: this.total,
      skipped: this.skipped || 0, skipAt: this.skipAt || [],
      ms: this.startedAt ? Math.round(egret.getTimer() - this.startedAt) : 0 });
    if (state.finished.length > 10) state.finished.shift();
    var idx, name;
    for (idx in this.cache) {
      if (!Object.prototype.hasOwnProperty.call(this.cache, idx)) continue;
      name = url(this.hero.dir, this.hero.files[idx]);
      delete this.cache[idx];
      release(name);
    }
    if (this.bitmap) this.bitmap.texture = null;
    if (this.container && this.container.parent) this.container.parent.removeChild(this.container);
    var active = state.active;
    for (var i = active.length - 1; i >= 0; i--) if (active[i] === this) active.splice(i, 1);
  };

  function heroFor(effect) {
    var name = baseName((effect && (effect._dbName || effect._action)) || '');
    var heroId = BY_KEY[name];
    if (heroId) {
      var hero = HEROES[heroId];
      if (!hero || !hero.frames || !hero.files || hero.files.length !== hero.frames) return null;
      return { id: heroId, hero: hero, key: name };
    }
    // Shared ultimate keys cannot name a hero on their own; the cast hook below
    // records which hero cast right before the effect is built.
    var pending = state.pending;
    if (!pending || egret.getTimer() - pending.at > 2500) return null;
    var owners = OWNERS[name];
    if (!owners) return null;
    for (var i = 0; i < owners.length; i++) {
      if (owners[i] === pending.heroId) {
        var h = HEROES[pending.heroId];
        if (!h || !h.frames || !h.files || h.files.length !== h.frames) return null;
        return { id: pending.heroId, hero: h, key: name };
      }
    }
    return null;
  }

  function casterHero(caster) {
    if (!caster) return null;
    var cfg = caster.config || caster.cfg || caster.heroConfig || caster.heroData || caster.heroVO;
    if (cfg) {
      var code = Number(cfg.code);
      if (isFinite(code) && code >= 41010000 && code < 41020000) return code - 41010000;
    }
    return null;
  }

  function keysOf(cfg) {
    if (!cfg) return null;
    var out = [];
    ['effectQP', 'effectSrc', 'effectsTarEnemy', 'effectsTarUs', 'effectsPiaUs', 'effectsPiaEnemy'].forEach(function (field) {
      var rows = cfg[field];
      if (!rows || !rows.length) return;
      for (var i = 0; i < rows.length; i++) {
        var src = rows[i] && rows[i].src;
        if (src && src.length) out.push(baseName(src[0]));
      }
    });
    return out.length ? out : null;
  }

  function noteCast(cfg, caster) {
    var heroId = casterHero(caster);
    if (!heroId) return;
    var hero = HEROES[heroId];
    if (!hero || !hero.allKeys) return;
    var keys = keysOf(cfg);
    if (!keys) return;
    for (var i = 0; i < keys.length; i++) {
      if (hero.allKeys.indexOf(keys[i]) >= 0) {
        state.pending = { heroId: heroId, at: egret.getTimer(), key: keys[i] };
        return;
      }
    }
  }

  function suppress(effect) {
    if (!effect) return;
    try {
      effect.visible = false;
      state.hidden++;
    } catch (e) { error('hide', e); }
  }

  function onTrigger(effect, action) {
    state.triggers++;
    var match = heroFor(effect);
    if (!match) return;
    state.matched++;
    state.lastMatch = { key: match.key, action: action || null,
      parent: effect.parent ? String(effect.parent.constructor && effect.parent.constructor.name) : null,
      timeScale: effect.timeScale || 1 };
    var now = egret.getTimer();
    var last = state.lastCast[match.id];
    if (last !== undefined && now - last < CAST_WINDOW_MS) {
      // Another layer of the same ultimate cast: keep it hidden, one overlay.
      suppress(effect);
      return;
    }
    state.lastCast[match.id] = now;
    suppress(effect);
    var overlay;
    try {
      overlay = new Overlay(match.id, match.hero, effect);
    } catch (e) {
      state.lastMatch.reason = 'throw';
      error('overlay', e);
      return;
    }
    if (!overlay.container || !overlay.container.parent) {
      state.lastMatch.reason = 'no-parent';
      return;
    }
    state.lastMatch.reason = 'started';
    state.overlays++;
    state.active.push(overlay);
    if (state.active.length > 6) state.active.shift();
  }

  function install() {
    if (state.installed) return true;
    if (!global.DBEffect || !DBEffect.prototype || typeof DBEffect.prototype.trigger !== 'function') return false;
    if (DBEffect.prototype.__streetUltimate) { state.installed = true; return true; }
    try {
      if (global.RES && typeof RES.setMaxLoadingThread === 'function' && !state.threads) {
        RES.setMaxLoadingThread(4);
        state.threads = true;
      }
    } catch (e) { /* optional */ }
    var original = DBEffect.prototype.trigger;
    DBEffect.prototype.trigger = function (action) {
      try { onTrigger(this, action); } catch (e) { error('hook', e); }
      return original.apply(this, arguments);
    };
    DBEffect.prototype.__streetUltimate = true;
    state.installed = true;
    return true;
  }

  function installCastHooks() {
    var g = global.game;
    var FT = g && g.FightTools;
    if (!FT || !FT.prototype) return false;
    if (FT.prototype.__streetUltimateCast) return true;
    ['handleEffectQP', 'handleEffectSrc', 'handleEffectTar'].forEach(function (name) {
      var original = FT.prototype[name];
      if (typeof original !== 'function') return;
      FT.prototype[name] = function (cfg, caster) {
        try { noteCast(cfg, caster); } catch (e) { error('cast', e); }
        return original.apply(this, arguments);
      };
    });
    FT.prototype.__streetUltimateCast = true;
    return true;
  }

  var timer = 0;
  var castTimer = 0;
  function boot() {
    var done = false;
    try { done = install(); } catch (e) { error('install', e); }
    if (!done && ++timer < 1800) setTimeout(boot, 100);
  }
  function bootCast() {
    var done = false;
    try { done = installCastHooks(); } catch (e) { error('installCast', e); }
    if (!done && ++castTimer < 1800) setTimeout(bootCast, 100);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { boot(); bootCast(); });
  } else {
    boot(); bootCast();
  }

  global.StreetUltimate = {
    install: install,
    installCastHooks: installCastHooks,
    noteCast: noteCast,
    snapshot: function () {
      return {
        installed: state.installed,
        triggers: state.triggers,
        matched: state.matched,
        hidden: state.hidden,
        overlays: state.overlays,
        frames: state.frames,
        heroCount: Object.keys(HEROES).length,
        keyCount: Object.keys(BY_KEY).length,
        lastMatch: state.lastMatch || null,
        finished: state.finished.slice(-4),
        active: state.active.map(function (o) {
          return { heroId: o.heroId, frame: o.frame, total: o.total, step: o.step,
                   onStage: !!(o.container && o.container.stage), visible: !!(o.bitmap && o.bitmap.visible) };
        }),
        errors: state.errors.slice(0, 8)
      };
    }
  };
})(window);
