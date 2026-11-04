"""Classify 86 characters' actual skills and prepare staged animation design tasks."""
import json
import re
from collections import Counter
from pathlib import Path
from classify_combat_actions import ROOT, OUT, read_model

EVIDENCE = json.loads((OUT/'original-evidence.json').read_text(encoding='utf-8'))

# These are observations of current replacement portraits, not historical weapons.
PROP_TEXT = '''1|徒手／手势|手指、拳掌
2|食物道具|手持食物
3|西瓜道具|西瓜
4|徒手／手势|双手合于胸前
5|徒手／拳脚|未见手持武器
6|刀盾|短刀、盾牌
7|单手剑|长剑
8|兽爪／拳脚|猫科造型、双爪
9|生活道具|外卖袋
10|徒手／腿脚|尖头鞋
11|徒手／手势|未见手持武器
12|徒手／手势|HP标识帽，无手持武器
13|警棍|当前仍显示原名称；立绘持警棍
14|生活道具|水杯、背包
15|徒手／手势|未见手持武器
16|锤|单手锤
17|笛／吹奏道具|横持吹奏道具
18|徒手／肘击|篮球服、双臂
19|徒手／掌法|掌法站姿
20|扇|羽扇
21|徒手／手势|未见手持武器
22|机械装置|机械手臂、胸口能量核心
23|徒手／拳脚|举拳姿势
24|生活道具|手机
25|短刃|单手短刃
26|徒手／拳脚|香蕉造型，无手持武器
27|生活道具|稻穗／草束
28|生活道具|话筒状手持道具
29|徒手／手势|蛙形角色，无手持武器
30|生活道具|计算器、购物袋
31|兽爪／拳脚|丧尸造型、双手
32|徒手／拳掌|咏春站姿
33|生活长柄道具|苍蝇拍
34|生活道具|橡果
35|机械装置|机械手臂、能量球状道具
36|徒手／拳脚|拳击站姿
37|生活道具|耳机、摊掌
38|徒手／手势|军装，无手持武器
39|扇|团扇
40|生活道具|钥匙串
41|食物道具|奶酪
42|手枪|单手短枪
43|徒手／拳脚|未见手持武器
44|炊具|平底锅／煎饼铛
45|符咒／徒手|额头符纸、僵尸前伸手
46|生活长柄道具|鱼竿、桶
47|生活道具|骨头
48|食物道具|烤串
49|植物道具|葱束
50|徒手／手势|未见手持武器
51|步枪|双手持长枪
52|投掷球体|篮球
53|徒手／拳脚|蛙装角色，无手持武器
54|符咒／法器|符纸、背负剑
55|徒手／手势|宫装，无手持武器
56|兽爪／徒手|鼠形角色，无手持武器
57|生活道具|手机
58|兽爪／拳脚|鲨鱼装角色，无手持武器
59|徒手／手势|新娘造型，无手持武器
60|生活长柄道具|占卜招牌
61|食物道具|鸡腿
62|兽爪／拳脚|鳄鱼装角色，无手持武器
63|生活道具|麻将牌
64|生活长柄道具|扫帚
65|兽爪／徒手|狐装角色、前伸双手
66|植物道具|白菜
67|扇|双扇
68|徒手／手势|张口、双手
69|徒手／手势|未见手持武器
70|待素材确认|当前角色表无可用立绘；名称为三叉戟将军
71|待素材确认|当前角色表无可用立绘；名称为青衣扇牛
72|待素材确认|当前角色表无可用立绘；名称为花脸枪牛
73|兽爪／拳脚|恐龙装角色，无手持武器
74|徒手／手势|头套造型，无手持武器
75|徒手／能量|变异造型，无手持武器
76|兽爪／拳脚|虎装角色，无手持武器
77|待素材确认|当前角色表无可用立绘；名称为佛系牛
78|徒手／手势|企鹅装角色，无手持武器
79|重刃|背负重刃、护甲
80|徒手／舞狮|舞狮造型
81|食物道具|胡萝卜
82|生活道具|眼镜状手持道具，需原图复核
83|能量球／龙息|手持火球
84|徒手／能量|蛇装角色，双臂交叉
85|食物道具|桃子
94|生活道具|手机'''
PROPS = {int(i):(kind,detail) for i,kind,detail in (line.split('|') for line in PROP_TEXT.splitlines())}
SAMPLES = {(18,'normalSkill'),(7,'normalSkill'),(16,'normalSkill'),(51,'normalSkill'),(4,'actSkill'),(29,'actSkill')}
BATCHES = [
 ('B01','六类样板动作','肘击、剑击、锤击、射击、群体治疗、单体护盾各1条','先制作关键姿势与事件表，再接入ComfyUI小样','角色不漂移；命中/发射/治疗/护盾各自对齐；游戏内验证后再铺开'),
 ('B02','近身普攻','目标前出手的普攻，按拳脚、刃器、重器、生活道具细分','沿用B01近身模板；角色根节点位移由引擎负责','保持接近与返回逻辑；不得在视频内重复冲到敌方'),
 ('B03','原地远程普攻','站位施法、投射与枪械普攻','发射动作与弹道、命中特效分别制作','发射不等于命中；保留弹道飞行时间'),
 ('B04','辅助动作与攻辅大招','被动改写的辅助普攻、治疗、净化、护盾、召唤、攻辅混合','先做原地辅助；赴友方与随机分支单独小样','友方与敌方标记分开；辅助不设计成砍击队友'),
 ('B05','单体与排级大招','单体、前排、后排、纵排大招','沿用武器模板；按实际目标范围分配特效','前排/后排/纵排不可替换成全屏伤害'),
 ('B06','多目标与全体大招','随机多目标、指定多目标、全体、中场释放','人物释放与场景特效分层制作','中场释放不等于逐个贴身；群体效果与结算顺序一致'),
 ('B07','特殊机制与多段大招','多段、冲刺穿越、隐显、重复动作、随机动作','逐条制作事件轨；用原始动作或动态回放验证','所有段数、顺序、移动及收招逐项验收'),
 ('B08','配置与素材复核','表现配置缺失、共享占位技能、新立绘缺失或身份未定','先锁定沿用配置或补齐素材，再迁入对应制作批次','不按角色名称擅自补造技能，不把兜底值当真实命中时间'),
]

def arr(v):
    if isinstance(v,list): return v
    try: return json.loads(v or '[]')
    except (ValueError,TypeError): return []

def targets(desc):
    if '进行一次占卜' in desc: return ('敌我分支全体' if '全体' in desc else '敌我分支单体'),'敌方或友方（按占卜结果）'
    if '召唤' in desc and '傀儡' in desc: return '召唤物／引爆分支','召唤物；引爆目标另核'
    ally=not bool(re.search(r'造成[^。；]*伤害|攻击敌方',desc))
    side='友方' if ally else '敌方'
    text=desc.split('并')[0].split('随后')[0]
    if ally and '自身' in text and not re.search(r'友方|我方',text):
        return ('自身＋友方全体' if re.search(r'(?:我方|友方)全体',desc) else '自身'),('自身＋友方' if re.search(r'(?:我方|友方)全体',desc) else '自身')
    if '单体' in text or ('单位' in text and not '全体' in text and not re.search(r'随机[234567]',text)): scope='单体'
    elif '全体' in text: scope='全体'
    elif '纵排' in text: scope='纵排'
    elif '后排' in text: scope='后排'
    elif '前排' in text: scope='前排'
    else:
        m=re.search(r'(随机|最低的|最高的)?([234567])(?:个|人)',text)
        scope=('随机' if '随机' in text else '指定')+m.group(2)+'目标' if m else '按技能机制'
    if '生成最多6只' in desc: return '友方受击触发／最多6只花灵','友方（触发式保护）'
    return scope,side

def purpose(desc):
    if '占卜' in desc: return '攻辅随机分支' if '伤害' in desc else '辅助／减益随机分支'
    if '召唤' in desc and '傀儡' in desc: return '召唤／引爆'
    damage=bool(re.search(r'造成[^。；]*伤害|攻击敌方',desc))
    if not damage: return '辅助'
    if re.search(r'(?:我方|友方|己方)(?:全体|单位|攻击|受到|上阵|附加)|回复(?:我方|友方)',desc):
        return '攻辅兼备'
    if re.search(r'回复自身|提高自身|自身受到|为自身|自身本次|本次攻击提高',desc):
        return '进攻＋自身增益'
    return '进攻'

def mech(desc):
    tags=[]
    for k in ['治疗','护盾','净化','恢复','流血','中毒','灼烧','眩晕','麻痹','沉默','混乱','嘲讽','挑衅','驱散','召唤','降低','窃取','铁索连环','真实伤害','秒杀','暴怒']:
        if k in desc: tags.append(k)
    if re.search(r'回复|恢复',desc) and '生命' in desc: tags.insert(0,'治疗/吸血')
    return '、'.join(dict.fromkeys(tags)) or '直接伤害'

def flatten_effects(perf):
    rows=[]
    for layer in ['effectSrc','effectQP','effectsTarEnemy','effectsTarUs','effectsTarUs2','effectsPiaEnemy','effectsPiaUs','effectFly','effectFlyArrive']:
        seq=perf.get(layer,[])
        if isinstance(seq,dict): seq=[seq]
        if not isinstance(seq,list): continue
        for ef in seq:
            if isinstance(ef,dict): rows.append((layer,ef))
    return rows

def movement(p,role):
    cfg=p.get('meFlyConfig')
    if not cfg: return '未解析（运行时可能使用无特效兜底）','待确认'
    n=cfg[0]
    loc={0:'原站位出手',1:'移到场地中部释放',2:'移到目标前出手',3:'分身接近目标',4:'中线预备＋自定义冲刺',5:'移到目标所在排前出手'}.get(n,'特殊位置')
    if any(x.get('type')=='customFly' for x in p.get('customAct',[]) if isinstance(x,dict)):
        return loc+'＋自定义移动','特殊移动'
    if role in ['辅助','攻辅随机分支','辅助／减益随机分支']:
        return loc, '赴友方辅助' if n in [2,5] else '辅助施法'
    projectile=any(e.get('type') in [1,2,3,4,5] for _,e in flatten_effects(p))
    if n in [2,5]: delivery='近身出手＋弹道/连线' if projectile else '近身攻击'
    elif n==0: delivery='远程弹道/连线' if projectile else '原地远程作用'
    elif n==1: delivery='中场释放（远近待回放）'
    else: delivery='特殊移动'
    return loc,delivery

def proposal(kind,role,scope,loc):
    if role=='辅助':
        body='收手蓄力→摊掌/抬手释放→收手待机'
    elif role=='召唤／引爆': body='双手凝聚→向地面释放→召唤显现；引爆另做分支'
    elif '随机分支' in role: body='起卦→揭示结果→吉凶分支分别触发友方/敌方特效'
    elif kind in ['单手剑','短刃','重刃','刀盾']:
        body='持刃蓄力→定向斩击→回收武器；盾牌与持握保持一致'
    elif kind=='锤': body='提锤蓄力→重击→短停顿→回收'
    elif kind in ['手枪','步枪']: body='举枪瞄准→开火后坐→复位；弹道独立'
    elif kind=='扇': body='收扇/引扇蓄力→挥扇释放→归位'
    elif kind=='生活长柄道具': body='长柄收势→前推/横扫→回收；鱼竿保留竿身柔性'
    elif kind in ['机械装置','能量球／龙息','徒手／能量']: body='核心/手部蓄能→定向释放→能量收束'
    elif kind=='投掷球体': body='收球蓄力→推掷→收手；球体与飞行轨迹独立'
    elif kind=='符咒／法器': body='结印/举符→释放符光→收势；背负剑不自动出鞘'
    elif kind=='笛／吹奏道具': body='举笛→吹奏释放→落手；声波独立'
    elif kind=='炊具': body='举锅蓄力→拍击/推送→回收'
    elif kind=='待素材确认': body='待立绘核对后选动作，不按名称补造武器'
    elif '道具' in kind: body='现有道具蓄势→挥动或释放能量→复位；不自动丢失道具'
    elif '兽爪' in kind: body='躯干蓄力→爪击/扑击上身姿势→回收'
    else: body='收臂蓄力→拳/掌/肘击→回到待机'
    if '目标前' in loc: root='引擎负责接近与返回；视频固定根位置，只做出手'
    elif '场地中部' in loc: root='引擎移到中场后播出手；视频不自行横穿战场'
    elif '自定义' in loc or '分身' in loc: root='移动/分身单独轨道，需逐条回放'
    else: root='原位播放，锁脚底锚点；位移若有由引擎负责'
    if scope in ['全体','前排','后排','纵排'] or '目标' in scope:
        body+='；命中覆盖由独立目标特效控制'
    return body,root

def weapon_clues(model):
    text=[]
    for arm in model.get('armature',[]):
        for row in arm.get('bone',[])+arm.get('slot',[]):
            name=row.get('name','')
            if re.search(r'wuqi|shanzi|yuxi|dadao|chui|qiang|gongjian|changjian|fuchen|qin',name,re.I): text.append(name)
    return '、'.join(dict.fromkeys(text))[:250] or '未取得明确武器命名；需看原动作'

def build():
    rows=[]; props=[]; effects_cache={}; effect_index={}
    for folder in ['model','effect','effect_f']:
        for p in (ROOT/'local_game/resource/assets'/folder).glob('*.bin'):
            effect_index.setdefault(re.sub(r'_[0-9a-f]{7,10}$','',p.stem),p)
    sample_lookup={}
    for r in EVIDENCE['records']:
        sid=r['heroId']; a=r['art']; base=r['base']; s=r['skill']; p=r['performance']
        passive_rewrites=[v for v in r.get('passives',[]) if v and re.search(r'普通攻击转[化变]为',v.get('desc',''))] if r['slot']=='normalSkill' else []
        passive_relevant=[v for v in r.get('passives',[]) if v and re.search(r'普通攻击|普攻|转化为|转变为|追击|连击',v.get('desc',''))]
        effective_desc=passive_rewrites[0]['desc'] if passive_rewrites else s.get('desc','')
        scope,side=targets(effective_desc); role=purpose(effective_desc); loc,delivery=movement(p,role)
        if role=='辅助' and side.startswith('自身') and p.get('meFlyConfig',[None])[0]==2:
            loc='自身目标原位（引擎跳过接近）'
            delivery='原位自身辅助'
        kind,detail=PROPS[sid]
        model=EVIDENCE['models'].get(base['model'],{}).get('data',{})
        action=p.get('modelAct') or ('gongji' if r['slot']=='normalSkill' else 'jineng')
        tim=next((x for x in model.get('_extractedTimelines',[]) if x['name']==action),{})
        events=tim.get('events',[])
        body,root=proposal(kind,role,scope,loc)
        if sid==18: body=body.replace('拳/掌/肘击','肘击')
        notes=[]
        shared=(s['modelId']=='common_skill_tianfeng_02' and sid!=69)
        if shared: notes.append('原包共用田丰大招表现/技能；保留实际配置，角色专属设计待核定')
        if not p: notes.append('原表现键在g_skill中不存在，需验证兜底路径')
        if kind=='待素材确认': notes.append('当前角色映射没有可用立绘，暂不锁定武器')
        if not a.get('matched'): notes.append('角色换皮映射未匹配；当前图与目标形象待核对')
        if a.get('originalName')=='未知': notes.append('原包角色身份未知，按角色ID关联')
        variants={v['modelId'] for v in r['variants'] if v}
        if len(variants)>1: notes.append('进阶存在不同表现键，需要分支验证')
        hits=[e for e in events if e.get('name') in ['pia','pia123','pia456']]
        launch=[e for e in events if e.get('name')=='zd']
        special=bool(p.get('customAct') or p.get('randModelActs') or p.get('forceExtraPlayTimes') or len(hits)>1 or '7段' in s.get('desc','') or p.get('forcePiaCount',1)>1)
        if shared or not p or kind=='待素材确认' or not a.get('matched'): batch='B08'
        elif (sid,r['slot']) in SAMPLES: batch='B01'
        elif role in ['辅助','辅助／减益随机分支'] and r['slot']=='normalSkill': batch='B04'
        elif r['slot']=='normalSkill': batch='B02' if '近身' in delivery or '目标前' in loc else 'B03'
        elif special: batch='B07'
        elif role in ['辅助','攻辅兼备','攻辅随机分支','召唤／引爆']: batch='B04'
        elif scope in ['单体','前排','后排','纵排']: batch='B05'
        else: batch='B06'
        ef_flat=flatten_effects(p)
        ef_types=[]
        for layer,ef in ef_flat:
            if layer=='effectQP': ef_types.append('场景/范围特效')
            elif layer=='effectSrc': ef_types.append('施法者特效')
            elif layer in ['effectFly','effectFlyArrive']: ef_types.append('移动伴随特效')
            elif layer.startswith('effectsPia'): ef_types.append('命中/生效附着特效')
            elif ef.get('type') in [1,4,5]: ef_types.append('飞行弹道')
            elif ef.get('type') in [2,3]: ef_types.append('连线/伸缩轨迹')
            else: ef_types.append('目标位置特效')
        semantic=mech(effective_desc)
        anchors=[]
        speed=p.get('modelActSpeedUp',1) or 1
        for e in hits:
            anchors.append(f"{e['name']}@{e['timeMs']/speed:.1f}ms（角色事件）")
        for e in launch:
            anchors.append(f"zd@{e['timeMs']/speed:.1f}ms（发射/启动特效）")
        impact_status='待整条技能回放验证'
        impact=[]
        if r['slot']=='normalSkill' and not special and len(hits)==1 and not launch:
            impact=[round(hits[0]['timeMs']/speed,3)]
            impact_status='角色pia直接回调；待游戏内验收'
        elif r['slot']=='normalSkill' and len(launch)==1 and not hits:
            bullets=[e for layer,e in ef_flat if layer=='effectsTarEnemy' and e.get('type') in [1,4,5] and isinstance(e.get('dt'),(int,float))]
            if bullets:
                impact=sorted({round(launch[0]['timeMs']/speed+e.get('delay',0)+e['dt'],3) for e in bullets})
                impact_status='发射事件＋弹道delay/dt推导；待游戏内验收'
        effect_details=[]
        for layer,ef in ef_flat:
            srcs=ef.get('src',[])
            if isinstance(srcs,str): srcs=[srcs]
            for src in srcs:
                info={'layer':layer,'resource':src,'delay':ef.get('delay',0),'dt':ef.get('dt'), 'timeScale':ef.get('timeScale',1), 'type':ef.get('type'), 'actionOverride':ef.get('action')}
                if src not in effects_cache:
                    path=effect_index.get(src)
                    try:
                        em=read_model(path) if path else {}
                        effects_cache[src]={'path':str(path.relative_to(ROOT)) if path else '', 'timelines':em.get('_extractedTimelines',[])}
                    except Exception as exc: effects_cache[src]={'error':str(exc)}
                info['asset']=effects_cache[src]
                effect_details.append(info)
        detail_txt=[]
        for e in effect_details:
            ev=[f"{v['name']}@{v['timeMs']:.1f}" for t in e['asset'].get('timelines',[]) for v in t['events'] if v.get('name') in ['pia','zd','pia123','pia456']]
            detail_txt.append(f"{e['layer']}: {e['resource']} delay={e['delay']} dt={e['dt']} speed={e['timeScale']}"+(' 事件='+','.join(ev) if ev else ''))
        status='设计待出样；分类已整理' if not notes else '需复核：'+'；'.join(notes)
        row={
            'taskId':f"H{sid:03}-{'ATK' if r['slot']=='normalSkill' else 'ULT'}",'heroId':sid,'name':a['name'],'originalName':a['originalName'],
            'slot':'普攻' if r['slot']=='normalSkill' else '大招','skillId':s['id'],'skillName':s['name'],
            'newSkillName':a.get('skills',{}).get(str(s['id']),{}).get('name',s['name']),
            'purpose':role,'targetSide':side,'scope':scope,'delivery':delivery,'movement':loc,'weapon':kind,'weaponObservation':detail,
            'effectClass':'、'.join(dict.fromkeys(ef_types)) or '角色动作/特殊机制（未列独立特效）','semantic':semantic,
            'bodyDesign':body,'rootPolicy':root,'batch':batch,'status':status,'reviewReasons':notes,
            'skillDesc':s.get('desc',''),'skillModel':s.get('modelId',''),'model':base['model'],'action':action,
            'effectiveDesc':effective_desc,'classificationStage':'被动改写生效后；解锁前仍用基础普攻' if passive_rewrites else '基础技能',
            'passiveRewrite':'\n'.join(f"{v['id']} {v['name']}：{v['desc']}" for v in passive_rewrites),
            'passiveNotes':'\n'.join(f"{v['id']} {v['name']}：{v['desc']}" for v in passive_relevant),
            'unlockConfig':base.get('skillUnlock',''),
            'originalWeaponClues':weapon_clues(model),'rawDurationMs':tim.get('durationMs'),
            'fps':tim.get('fps'),'durationFrames':tim.get('durationFrames'),'rawEvents':events,
            'modelSpeed':speed,'animationScale':tim.get('scale',1),'eventText':'；'.join(anchors) or '角色轨无pia/zd，需追踪特效/特殊逻辑',
            'impactMs':impact,'impactStatus':impact_status,'performance':p,'effectDetails':effect_details,
            'effectText':'\n'.join(detail_txt),'variants':sorted(variants),'portrait':a.get('portrait',''),
        }
        rows.append(row)
        if (sid,r['slot']) in SAMPLES: sample_lookup[sid]=row
        if r['slot']=='normalSkill': props.append({'heroId':sid,'name':a['name'],'originalName':a['originalName'],'weapon':kind,'observation':detail,'originalClues':weapon_clues(model),'portrait':a.get('portrait',''),'verified':'立绘观察，需动作样片复核' if kind!='待素材确认' else '缺少立绘'})
    samples=[]
    designs={
      18:('肘击近身单体','上身略后收，前臂折叠','肘尖向敌方短促送出，胸腰同向转动','收肘回站姿，双脚回原锚点','短冲击波＋目标接触闪光；不生成第二个角色'),
      7:('单手剑近身单体','持剑手回收，刃口朝预定劈砍方向','单次斜斩，剑长与握持不变','沿原路线回收，回待机','剑光独立一层；不新增连击或换手'),
      16:('重锤近身单体','握锤提起，重心略下沉','锤头向前下方重击，接触瞬间短停顿','反向提回，保持锤头形状','接触尘圈＋碎光；不做大幅全屏震动'),
      51:('步枪原地远程单体','双手握枪，枪口对敌方','扣扳机时枪身后坐一次','枪身回稳，双手与枪托不分离','枪口火光、飞行弹道、目标命中三层分开'),
      4:('原地群体治疗','双手胸前收拢蓄力','摊掌释放，表情与身体朝友方','手臂落回原待机姿势','人物柔光＋友方治疗光；禁止敌方爆炸表现'),
      29:('原地单体净化护盾','蛙形角色抬手聚光','向选中友方送出保护能量','收手回待机，脚底位置不变','净化闪光与护盾成形分层，护盾随目标保留'),
    }
    for sid in [18,7,16,51,4,29]:
        r=sample_lookup[sid]; template,prep,key,recover,fx=designs[sid]
        t=r['impactMs'][0] if r['impactMs'] else None
        if sid==51:
            control='500ms发射；750ms为标准1倍速弹道命中推导值（500+250），待游戏内验收'
        elif t is not None: control=f"动作播放起点为0；{t:.3f}ms对齐接触姿势；位移阶段另计"
        else: control='角色技能轨无生效事件；按已提取特效轨定位，动态回放后再锁生效时间'
        samples.append({'taskId':r['taskId'],'heroId':sid,'name':r['name'],'slot':r['slot'],'template':template,'prep':prep,'keyPose':key,'recovery':recover,'fx':fx,'timing':control,'rootPolicy':r['rootPolicy'],'durationMs':r['rawDurationMs'],'status':'动作设计与参数已整理；尚未生成视频',
          'prompt':f"以输入角色图为唯一外观参考，保持现有服装、体型和道具。固定游戏镜头，全身完整可见，保持输入图背景。完成一次{template}动作：{prep}，然后{key}，最后{recover}。脚底锚点稳定，不移动相机，不出现其他角色，不把特效画进人物主体。后期按事件表对齐时间；提示词中的时间不视为精确控制。"})
    counts=Counter(r['batch'] for r in rows)
    batchrows=[]
    for bid,title,scope,method,accept in BATCHES:
        tasks=[r for r in rows if r['batch']==bid]
        batchrows.append({'id':bid,'title':title,'count':counts[bid],'scope':scope,'method':method,'acceptance':accept,
                          'taskIds':[r['taskId'] for r in tasks],'members':'、'.join(f"{r['name']}·{r['slot']}" for r in tasks),
                          'status':'设计规范已整理，待工作流接入' if bid=='B01' else '待出样' if bid!='B08' else '待配置/素材复核'})
    result={'date':'2026-10-22','heroCount':len(props),'actionCount':len(rows),'rows':rows,'props':props,'batches':batchrows,'samples':samples,
            'counts':dict(counts),'sourcePaths':['outputs/game-config-summary/staging/records.ndjson','local_game/character-reskin-data.js','local_game/resource/config/g_skill_96a92798.json','local_game/resource/assets/model/','recovered_runtime/main.formatted.js','local_game/js/all.min_32285d70.js'],
            'methodNotes':[
              '范围按技能实际描述与SkillBaseLO/SkillEffectLO关联整理。普攻有改写被动时按改写生效后的行为分类，另保留解锁前基础普攻描述；解锁条件需随skillUnlock和实战验证。',
              'meFlyConfig：0原位、1中场、2目标前、3分身、4中线穿越、5目标所在排前。辅助技能的目标前可指友方，不等同近身攻击。',
              '新武器分类来自当前替换立绘观察；原武器命名线索仅用于回查，不冒充已验证武器。生活道具不强行换成原武器。',
              '角色动画时长与事件由原始DragonBones二进制直接解码。frame0以0起算，ms按该骨架帧率换算；非游戏全流程耗时。',
              'pia、zd按运行路径解释。普攻zd通常启动特效/弹道；远程命中需叠加delay与dt，不能将发射帧当命中帧。',
              '大招的命中可能在场景/目标特效或自定义逻辑中。表中角色事件、特效局部事件与最终生效时间分列；空白不代表0ms。',
              'modelActSpeedUp、动画scale、战斗倍速、到位、重复播放、加载及随机分支影响实际节奏。推导值以标准1倍速资源就绪为前提，须游戏内验收。',
              'attackFrameDelay、attackDoneDelay、allAttkDelayOffset属于配置计时/兜底或结束相关字段，不直接当真实命中时间。__或_开头备份字段不作为启用配置。',
              'B01为6条样板动作设计，不代表已生成动画。其余166条进入B02—B08，复核项可在确定后移入对应制作批次。',
              '人物动作尽量固定根节点；引擎接近/返回、弹道、目标特效、场景特效分轨，保留原版结算逻辑。',
              '新动作可改变视觉表达，目标选择、段数、伤害、辅助机制不因换皮改变。近战原位出手素材仍可由引擎移动后在目标前播放。',
            ]}
    assert len(props)==86 and len(rows)==172
    assert len({r['taskId'] for r in rows})==172 and sum(counts.values())==172
    assert all(r['skillId'] and r['weapon'] and r['scope'] and r['batch'] for r in rows)
    for r in rows:
        assert all(0<=ev['frame0']<=r['durationFrames'] for ev in r['rawEvents'])
    (OUT/'combat-action-plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    for b in batchrows:
        folder=OUT/'batches'/b['id']; folder.mkdir(parents=True,exist_ok=True)
        (folder/'tasks.json').write_text(json.dumps({'batch':b,'tasks':[r for r in rows if r['batch']==b['id']]},ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'batches/B01/sample-designs.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'heroes':len(props),'actions':len(rows),'batches':dict(counts),'bodyEventRows':sum(bool(r['rawEvents']) for r in rows),'inferredImpactRows':sum(bool(r['impactMs']) for r in rows),'effectsDecoded':sum(bool(x.get('timelines')) for x in effects_cache.values()),'effectsMissing':sum(not x.get('timelines') for x in effects_cache.values())},ensure_ascii=False))
    print('FIRST_BATCH',json.dumps([{k:s[k] for k in ['taskId','name','timing']} for s in samples],ensure_ascii=False))

if __name__=='__main__': build()
