(function(global){
 'use strict';
 var installed=false,audit={installed:false,buttons:{}};
 function sync(button,id,cfg){
  if(!button||!button.gp_unlock)return;
  var state=Utils.UnlockMgr.checkPass(cfg.unlockModule,false);if(!state||typeof state.allow!=='boolean')return;
  button.gp_unlock.visible=!state.allow;
  if(button.lbl_toast)button.lbl_toast.text=state.allow?'':String(state.ext&&state.ext.desc||'尚未开放');
  if(id===game.MODULE.Hero&&button.lbl_name)button.lbl_name.text='街坊';
  audit.buttons[id]={allowed:state.allow,lockVisible:button.gp_unlock.visible,toast:button.lbl_toast&&button.lbl_toast.text};
 }
 function install(){
  if(installed||!global.game||!game.MainUI)return;
  var p=game.MainUI.prototype,created=p.childrenCreated;
  p.childrenCreated=function(){
   var result=created.apply(this,arguments),view=this;
   Object.keys(game.MainBtnConfig.BOTTOM_BTN_CONFIG).forEach(function(id){
    var cfg=game.MainBtnConfig.BOTTOM_BTN_CONFIG[id],button=view.getBottomBtn(Number(id));if(!button)return;
    if(button.gp_unlock)sync(button,Number(id),cfg);
    else button.once(eui.UIEvent.CREATION_COMPLETE,function(){sync(button,Number(id),cfg);},view);
   });
   return result;
  };
  installed=audit.installed=true;
 }
 global.OfflineNavigationState={install:install,audit:audit};
})(window);
