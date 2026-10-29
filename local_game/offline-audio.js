(function(global){
 'use strict';
 if(!global.HTMLMediaElement||global.OfflineAudio)return;
 var original=HTMLMediaElement.prototype.play,originalPause=HTMLMediaElement.prototype.pause,pending=[],stopped=new WeakSet(),audit={blocked:0,resumed:0,discarded:0,failures:[]};
 function blocked(media){audit.blocked++;if(stopped.has(media))return;var src=media.currentSrc||media.src;pending=pending.filter(function(row){return row.media!==media&&row.src!==src;});pending.push({media:media,src:src,time:Date.now()});if(pending.length>16){pending.shift();audit.discarded++;}}
 HTMLMediaElement.prototype.pause=function(){stopped.add(this);var media=this;pending=pending.filter(function(row){return row.media!==media;});return originalPause.apply(this,arguments);};
 HTMLMediaElement.prototype.play=function(){
  var media=this;stopped.delete(media);var result=original.apply(media,arguments);
  return result&&result.catch?result.catch(function(error){if(error&&error.name==='NotAllowedError'){blocked(media);return;}throw error;}):result;
 };
 function resume(){
  pending.splice(0).forEach(function(row){
   var media=row.media;if(stopped.has(media)||row.src!==(media.currentSrc||media.src)||(!media.loop&&!(media.duration>=8)&&Date.now()-row.time>1000)){audit.discarded++;return;}
   var result=original.call(media);if(result&&result.then)result.then(function(){audit.resumed++;},function(error){if(error&&error.name==='NotAllowedError')blocked(media);else audit.failures.push(String(error));});
  });
 }
 document.addEventListener('pointerdown',resume,true);document.addEventListener('keydown',resume,true);
 global.OfflineAudio={snapshot:function(){return {blocked:audit.blocked,resumed:audit.resumed,discarded:audit.discarded,pending:pending.length,failures:audit.failures.slice()};}};
})(window);
