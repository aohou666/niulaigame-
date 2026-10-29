(function(global){
 'use strict';
 var installed=false,audit={installed:false,ignoredStartupMarkers:[],forwardedImpactEvents:0};
 // Recovered 082_03 has an immediate pia marker and a second actual gesture pia.
 // The once-trigger battle callback previously consumed the immediate marker and
 // returned to idle around native frame10, before the authored frame28/31 gesture.
 // Keep the native event stream intact; only defer this battle callback.
 var paired={hero_082_03:{gongji:28,jineng:31},hero_082_03_ez:{gongji:28,jineng:31}};
 function install(){
  if(installed||!global.DBPlayer)return;
  var p=DBPlayer.prototype,original=p.frameHandler;
  p.frameHandler=function(event){
   var expected=paired[this._dbName],frame=expected&&expected[this.action],object=event&&event.eventObject;
   if(frame&&object&&object.name==='pia'&&Number(object.time)===0){
    if(audit.ignoredStartupMarkers.length<100)audit.ignoredStartupMarkers.push({model:this._dbName,action:this.action,markerTime:object.time,impactFrame:frame});
    return;
   }
   if(frame&&object&&object.name==='pia')audit.forwardedImpactEvents++;
   return original.apply(this,arguments);
  };
  installed=audit.installed=true;
 }
 global.OfflineHitEvents={install:install,audit:audit};
})(window);
