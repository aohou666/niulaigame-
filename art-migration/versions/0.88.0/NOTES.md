
## v0.88：独立受击21帧接入与真实装备战斗修复
100201新增shouji：官方21个独立绘制源帧逐帧映射原生21@30=0.7秒，图集1162x780、RGBA解码3625440字节；新StreetBodyData.skins独立注册，不覆盖基础2。明确主armature hero_skin_002_01，只作用普通/EZ主骨架，effect_1/2/3不绑定人物body/idle。错误id/缺armature/重复模型骨架配置保留原生，不污染base2缓存，三负面fixture通过。
原生42项暂停帧映射、普通/EZ实播均观察21不同帧、约0.7秒、原生完成回调1次/无 authored frame events，全部21×2接触图及放大峰值已看，连续一次侧倒回正和道具数正确；切回独立idle、未替换攻技跑步原生回退、6特效骨架、复用/销毁0body缓存通过。首次暂停切动作测试发现旧idle.hidden保留会让未映射gongji立即采样时native也隐藏；render显式清理未映射非idle状态，已修并保留before-fix证据。
真实HeroDermaPutOn代理/服务器存档保存已装备100201后，demo构造实体仍dermaCode0，before报告复现。configureOriginalBattleEntity现在带入有效同subType皮肤；applyLocalHangUpEntity也从硬编码0修复。实际主入口打开HangUpSystemMed.MAIN，原生挂机载荷携带100201；真实PutDown后reload载荷归0，通过且隔离存档恢复/主存档不变。
最初数次真实战斗受击测试超时（before/after/slow-fixture/native-stage10均保留）；原战报113个指向该角色的结果没有负伤害，多次敌方攻击均标MISS。local fillLocalAdvancedAttrs以整数百分数生成Miss43，原生BattleAIAttrData直接用value，isHit公式max(0,1+Hit-Miss)，误读为43而非0.43。新增offline-battle-attributes.js只将明确标记的离线英雄/支援UI百分数在深拷贝AI输入中转比率，保留存档/展示实体/Atk Life Defence Speed Anger及未标记原生敌方属性；marker阻止重复转换。单元和实际AI审计43→0.43，真实负伤害出现。八敌/单敌两真实BattleAI战斗均触发新受击（分别10/9不同源帧在战斗打断前观察到，非声称实际每次战斗都完整21帧；完整21@0.7秒另有原生播放器实播证明），截图已看，原作未换特效仍可遮挡人物。不人工trigger命中、不改战报。
本机15秒普通/EZ双循环图集共享1份/users2，均21不同帧，P95约16.8ms，>100ms帧0；销毁0body缓存。只本机Chrome预热播放，不是APK/手机/所有战斗无卡顿保证。
两套85最终复查均85/85（当前83新base+2原作未换独立皮肤，基础85新idle），1876原有动作/14特效/125属性4卡台面/6副骨架/100202双9秒原生fit与独立切换/1913依赖全台账通过，85静态肖像4页已实际看并保存SHA。没有绑定错/缺原包文件。完整角色0/85、完整独立皮肤0/125不变；100201只有4独立静态、连续idle、这1个受击动作，攻技跑步和3特效仍缺。历史DETAIL-NULL/RESOURCE-LOAD-015/TEMPORAL、地图纵向拉伸issue不据此关闭。
Comfy实际队列空，无活动生成。下一实质版本v89，届时推87/88/89并核远端；远端仍v86 SHA75849ddce72158771c0fdf4e87853a3d09683f90。拒收MiniMax片段保留，不再称运行。
