/* Skill-FX reskin runtime.
 *
 * Two mechanisms, because the effect keys split into two groups:
 *
 * 1) SINGLE-consumer keys (226 of 245). The key backs exactly one hero, so the key itself is
 *    redirected: RES is wrapped so that "<key>_bin" loads our recoloured container. That covers every
 *    engine path (pia impact, target effect, fly effect, special controllers), because they all end in
 *    AssetsMgr.getResAsync -> RES.getResAsync("<dbName>_bin"). No per-hero logic involved.
 *
 * 2) SHARED keys (19 keys, 92 job references). g_skill is keyed by the skill id and cannot be edited
 *    per hero, so those stay a per-caster rewrite at the battle effect entry point.
 *
 * Both sets of containers keep the ORIGINAL data/armature/animation/atlas names; only texture pixels
 * differ, so the engine's name resolution (getDBFileName -> initEffect(dbFileName, src)) is unchanged
 * and the clock is byte-identical to the original.
 */
(function (global) {
  'use strict';
  var RESOURCES = global.StreetFXResources || [];
  var REDIRECT = global.StreetFXRedirect || {};
  var TABLE = global.StreetFXBatchTable || {};
  var audit = { resReady: false, resWrapped: false, resources: null, redirected: 0,
                installed: false, calls: 0, overridden: 0, debug: [], casterProbe: null };

  function registerResources() {
    if (!global.RES || !RES.config || typeof RES.config.addResourceData !== 'function') return false;
    var added = 0, failed = 0;
    for (var i = 0; i < RESOURCES.length; i++) {
      var r = RESOURCES[i];
      try {
        if (!RES.hasRes(r.name)) {
          RES.config.addResourceData({ name: r.name, url: r.url, type: 'bin', root: '' });
          added++;
        }
      } catch (e) { failed++; }
    }
    audit.resources = { total: RESOURCES.length, added: added, failed: failed };
    var missing = 0;
    for (var j = 0; j < RESOURCES.length; j++) {
      try { if (!RES.hasRes(RESOURCES[j].name)) missing++; } catch (e) { missing++; }
    }
    audit.missing = missing;
    audit.resReady = missing === 0;
    return audit.resReady;
  }

  function allWrapped() {
    return audit.resWrapped && audit.resReady;
  }

  function wrapRes() {
    if (audit.resWrapped) return true;
    if (!global.RES || typeof RES.getRes !== 'function' || typeof RES.getResAsync !== 'function') return false;
    var getRes = RES.getRes;
    var getResAsync = RES.getResAsync;
    RES.getRes = function (name) {
      var target = REDIRECT[name];
      if (target) {
        audit.redirected++;
        return getRes.apply(RES, [target].concat(Array.prototype.slice.call(arguments, 1)));
      }
      return getRes.apply(RES, arguments);
    };
    RES.getResAsync = function (name) {
      var target = REDIRECT[name];
      if (target) {
        audit.redirected++;
        return getResAsync.apply(RES, [target].concat(Array.prototype.slice.call(arguments, 1)));
      }
      return getResAsync.apply(RES, arguments);
    };
    audit.resWrapped = true;
    return true;
  }

  function heroOf(model) {
    if (!model) return null;
    var cfg = model.config || model.cfg || model.heroConfig || model.heroData || model.heroVO;
    if (cfg) {
      var code = Number(cfg.code);
      if (isFinite(code) && code >= 41010000 && code < 41020000) return code - 41010000;
    }
    var cands = [model.heroId, model.heroCode, model.subType, model.code];
    var names = [model.model, model.modelName, model.resName, model.dbName, model._dbName, model.skin];
    for (var i = 0; i < names.length; i++) {
      var m = /hero_0*(\d+)/.exec(String(names[i] || ''));
      if (m) cands.push(Number(m[1]));
    }
    for (var j = 0; j < cands.length; j++) {
      var v = cands[j];
      if (typeof v === 'number' && isFinite(v) && v > 0) return v;
      if (typeof v === 'string' && /^\d+$/.test(v)) return Number(v);
    }
    return null;
  }

  function allyCaster(caster) {
    if (!caster) return false;
    if (caster.camp === undefined || caster.camp === null) return true;
    return String(caster.camp) === '1';
  }

  function probeCaster(caster) {
    if (audit.casterProbe || !caster) return;
    var out = {};
    ['camp', 'entityId'].forEach(function (f) { if (caster[f] !== undefined) out[f] = String(caster[f]); });
    var cfg = caster.config;
    if (cfg) { out.code = String(cfg.code); out.subType = String(cfg.subType); }
    audit.casterProbe = out;
  }

  function mapKey(key, hero) {
    var byHero = TABLE[key];
    if (!byHero) return null;
    return byHero[String(hero)] || null;
  }

  function rewrite(branch, hero) {
    if (!branch || !branch.length) return null;
    var changed = false;
    var next = branch.map(function (row) {
      if (!row || !row.src || !row.src.length) return row;
      var db = mapKey(row.src[0], hero);
      if (!db) return row;
      changed = true;
      var clone = {};
      for (var k in row) if (Object.prototype.hasOwnProperty.call(row, k)) clone[k] = row[k];
      clone.src = [db].concat(row.src.slice(1));
      return clone;
    });
    return changed ? next : null;
  }

  function decorate(cfg, hero) {
    var enemy = rewrite(cfg.effectsPiaEnemy, hero);
    var us = rewrite(cfg.effectsPiaUs, hero);
    if (!enemy && !us) return cfg;
    var out = {};
    for (var k in cfg) if (Object.prototype.hasOwnProperty.call(cfg, k)) out[k] = cfg[k];
    if (enemy) out.effectsPiaEnemy = enemy;
    if (us) out.effectsPiaUs = us;
    audit.overridden++;
    return out;
  }

  function install() {
    if (audit.installed) return true;
    var g = global.game, FT = g && g.FightTools;
    if (!FT || !FT.prototype || typeof FT.prototype.handleOnPia !== 'function') return false;
    if (FT.prototype.__streetFXDispatch) { audit.installed = true; return true; }

    var original = FT.prototype.handleOnPia;
    FT.prototype.handleOnPia = function (caster, target, cfg, scale) {
      audit.calls++;
      try {
        if (cfg) {
          probeCaster(caster);
          var hero = allyCaster(caster) ? heroOf(caster) : null;
          var next = decorate(cfg, hero);
          if (audit.debug.length < 40) {
            var keys = [];
            (cfg.effectsPiaEnemy || []).forEach(function (r) { if (r && r.src) keys.push(r.src[0]); });
            audit.debug.push({ hero: hero, changed: next !== cfg, keys: keys.slice(0, 2) });
          }
          if (next !== cfg) return original.call(this, caster, target, next, scale);
        }
      } catch (err) {
        audit.error = String((err && err.message) || err);
      }
      return original.call(this, caster, target, cfg, scale);
    };
    FT.prototype.__streetFXDispatch = true;
    audit.installed = true;
    return true;
  }

  var resTimer = 0, ftTimer = 0, configHooked = false, reapplyUntil = 0, reapplied = 0;
  /* The game loads its resource config AFTER this script runs. Adding resources before that point
   * leaves them in a temporary config that the real load replaces, so the window is re-registered
   * from the loadConfig completion hook and re-checked for a while afterwards. */
  function hookConfigLoad() {
    if (configHooked || !global.RES || typeof RES.loadConfig !== 'function') return false;
    configHooked = true;
    var load = RES.loadConfig;
    RES.loadConfig = function () {
      var ret = load.apply(this, arguments);
      function after(value) { registerResources(); reapplied++; return value; }
      if (ret && typeof ret.then === 'function') return ret.then(after);
      registerResources(); reapplied++;
      return ret;
    };
    return true;
  }
  function bootRes() {
    try {
      hookConfigLoad();
      if (wrapRes()) {
        var ready = registerResources();
        if (ready) {
          if (!reapplyUntil) reapplyUntil = Date.now() + 60000;
        } else {
          reapplied++;
        }
      }
    } catch (e) {
      audit.error = 'res:' + String((e && e.message) || e);
    }
    var keepChecking = reapplyUntil && Date.now() < reapplyUntil;
    if (!audit.resReady || keepChecking || ++resTimer < 1200) setTimeout(bootRes, 250);
  }
  function bootFT() {
    try {
      if (install()) return;
    } catch (e) {
      audit.error = 'ft:' + String((e && e.message) || e);
    }
    if (++ftTimer < 1800) setTimeout(bootFT, 100);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { bootRes(); bootFT(); });
  } else { bootRes(); bootFT(); }

  global.StreetFXDispatch = {
    install: install,
    probe: decorate,
    snapshot: function () {
      return { resWrapped: audit.resWrapped, resResources: audit.resources,
               redirected: audit.redirected, installed: audit.installed,
               calls: audit.calls, overridden: audit.overridden, error: audit.error || null,
               redirects: Object.keys(REDIRECT).length, tableKeys: Object.keys(TABLE).length,
               configHooked: configHooked, reapplied: reapplied,
               casterProbe: audit.casterProbe, debug: audit.debug.slice(0, 12) };
    }
  };
})(window);
