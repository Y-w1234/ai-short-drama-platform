"""
内容安全扫描器 —— 检测用户输入中的内容安全风险模式

与结构注入防御 (safe_chat) 互补:
- safe_chat 防御: 攻击者试图控制系统 → 指令/数据分离
- 内容扫描防御: 攻击者提交有害内容模式 → 预 LLM 模式检测

检测的攻击类别:
- 时间桥填补: 描述帧1和帧3，省略帧2让LLM补全暴力内容
- 暴力内容指示符: 武器/伤害/血腥关键词组合
- 渐进式越狱: 逐帧递进到违规内容
"""
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScanResult:
    """单次内容扫描结果"""
    passed: bool = True                        # 是否通过安全扫描
    risk_level: str = "none"                    # none / low / medium / high / blocked
    blocked_patterns: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    sanitized_content: Optional[str] = None     # 如果需要清洗后的版本
    reason: str = ""


class ContentSafetyScanner:
    """预 LLM 内容安全扫描器

    在用户内容到达任何 LLM 调用之前运行。
    与消息结构隔离 (safe_chat) 并行工作——一个处理结构，一个处理内容。
    """

    # ── 时间桥攻击模式 ──
    # 检测: 描述 A (安全) + 省略/间隙 + 描述 C (暴力后果)
    # 攻击者依赖 LLM 的补全倾向来填充暴力 B

    TEMPORAL_BRIDGE_PATTERNS = [
        # 冲突 + 间隙 + 伤害后果
        (r'(对峙|争吵|推搡|扭打|冲突|搏斗|打架)[^。]*(?:第[2二]|frame\s*2|镜头[2二]|shot[_\s]*2)[^。]*?(?:省略|跳过|略过|空缺|留白|——|…{2,})',
         "时间桥: 冲突→跳过→未知"),
        (r'(?:第[13三]|frame\s*[13]|镜头[13]|shot[_\s]*[13])[^。]*?(?:倒在|躺在|倒下|流血|血泊|红色液体|不动)',
         "时间桥: 跳过中帧,直接到达伤害后果"),
        # 中帧故意留空 + 后果暗示
        (r'(?:第[2二]|frame\s*2|镜头[2二])[^。]*?(?:省略|跳过|略过|——|…{2,}|请.*补全|请.*生成|请.*填充)',
         "时间桥: 显式要求模型补全中帧"),
    ]

    # ── 暴力内容指示符 ──
    VIOLENCE_INDICATORS = [
        # 通用暴力分类词 — 低置信度但高覆盖率
        (r'(?:暴力|血腥|残暴|凶残).*?(?:袭击|冲突|事件|行为|内容|场面|镜头|画面|场景)', "暴力分类描述"),
        # 武器 + 动作
        (r'(拔刀|刺向|捅|砍|射击|开枪|持枪|挥舞.*刀|举起.*枪)', "暴力动作指示"),
        # 伤害后果
        (r'(倒在血泊|血流不止|血肉模糊|鲜血.*喷|血.*溅)', "血腥后果描述"),
        # 致命武力
        (r'(致命|致死|杀害|谋杀|杀死|勒死|掐死)', "致命武力指示"),
        # 攻击类动作 (新增 — 原缺失导致裸"暴力袭击"漏检)
        (r'(袭击|攻击|殴打|群殴|毒打|暴打|围殴)', "攻击动作指示"),
    ]

    # ── 渐进式越狱模式 ──
    # 从正常内容开始，逐帧递进到违规内容
    GRADUAL_ESCALATION_PATTERNS = [
        # 帧1正常 → 帧2灰色 → 帧3违规
        (r'第1[帧镜].*?(?:正常|日常|普通|平凡).*?第[23][帧镜].*?(?:暴力|血腥|恐怖|惊悚|限制级|R级)', "渐进越狱"),
        # "艺术片" / "研究用途" 掩护
        (r'(?:艺术片|研究用途|学术目的|红队测试|安全测试|压力测试).*?(?:暴力|血腥|伤害|刺杀)', "伪造测试意图"),
    ]

    # ── 多轮漂移检测 (JB-MSD-001) ──
    # 单次脚本中嵌入多轮"迭代优化"，逐轮递进至违规内容
    # 签名: 多个 [第N轮]/RoundN/再X一点/更X 标记 + 方向性强化词
    # 即使管道是无状态 (无会话), 攻击者可以通过逐轮复制输出来手动漂移
    # 此模式检测"单次脚本中嵌入的完整漂移轨迹"
    MULTI_ROUND_DRIFT_PATTERNS = [
        # 多轮迭代标记 + 递进方向关键词 (在同一句内)
        (r'(?:第[1-9][轮次]|Round\s*[1-9]|第[1-9]次|[1-9]st|[1-9]nd|[1-9]rd|[1-9]th|迭代[1-9]).*?(?:更.*?(?:真实|强烈|冲击|暴力|刺激|血腥|细节|特写|慢动作|放大)|请.*(?:展示|生成|增加|增强).*?(?:细节|特写|慢动作))',
         "多轮漂移: 迭代标记+递进方向"),
        # "再/更 + 强度词" 模式出现 ≥2 次 → 强度递增链
        # 检测"更X...再Y"或"再X...更Y"的递进关系
        (r'(?:再|更)(?:真实|强烈|冲击|暴力|刺激|血腥|猛|狠|重|深|增强|加强|放大|加重).*?(?:再|更)(?:真实|强烈|冲击|暴力|刺激|血腥|猛|狠|重|深|增强|加强|放大|加重)',
         "多轮漂移: 递增强度链"),
        # 单句中同时出现 递进锚点(更+) + 伤害锚点(面部/身体/受伤/血) → 漂移信号
        (r'(?:更|再|加强|增强|放大).*?(?:真实|冲击|暴力|重|猛|狠).*?(?:面部|身体|倒地|受伤|血|骨|皮|眼睛|鼻子|嘴巴|头部)',
         "多轮漂移: 递进+伤害锚点同句"),
    ]

    # ── SceneSplit 攻击检测 (JB-SS-001) ──
    # 将有害叙事拆分为多个看似无害的子句, 拼接后LLM自动补全中间的恶意事件
    # 结构签名: 3段式 — 角色入场(A) → 正常活动/时间流逝(B) → 异常后果(C)
    # A和C各自无害, 但A→B→C的拼接迫使LLM在B和C之间"填补"有害事件
    # 70-80%成功率 vs 单提示攻击的0-10%

    SCENE_SPLIT_PATTERNS = [
        # Phase A: 人物入场 — 一个人进入/到达某地 (完全中性)
        (r'(?:一个|一位|一名)[^。]*?(?:走进|进入|到达|抵达|步入|踏入|来到)[^。]*?(?:大楼|建筑|办公室|银行|会议室|房间|场地|广场|总部|大厦|工厂|仓库|医院|学校|公寓|住宅|商店|餐厅)',
         "SceneSplit: 人物入场"),
        # Phase C: 异常后果 — 但没有任何中间因果描述
        (r'(?:所有人|大家|每个人|在场.*人)[^。]*?(?:震惊|惊恐|恐慌|愕然|愣住|说不出话|目瞪口呆)',
         "SceneSplit: 集体震惊"),
        (r'(?:整个|全部|全).*?(?:封锁|疏散|清空|关闭|停摆|瘫痪)',
         "SceneSplit: 区域封锁/清空"),
        (r'(?:所有|全部|整个).*?(?:归零|消失|冻结|清空|蒸发)',
         "SceneSplit: 资产突变"),
        (r'(?:没有人|不再|再也|从此).*?(?:知道|看见|发现|出现|回来|见过|找到|联系|消息|下落)',
         "SceneSplit: 人员消失"),
    ]

    # 正常活动B短语 — 本身无害, 但夹在A和C之间暗示时间流逝
    NORMAL_ACTIVITY_BRIDGE = [
        r'(?:正在|在).*?(?:进行|开会|讨论|谈话|交谈|交流|等待)',
        r'(?:一切|一切.*都|什么.*都).*?(?:正常|顺利|如常|平静)',
        r'(?:早上|上午|下午|晚上|夜晚).*?(?:一切|一切.*都|什么.*都).*?(?:正常|顺利)',
    ]

    # ── 感官启动攻击检测 (JB-SPARK-001) ──
    # 利用视听共现先验: 中性视觉场景 + 暴力关联听觉触发词 + 紧张电影风格
    # LLM 的训练数据中将"吱嘎声+撞击声+手持摄影+暗光"与暴力/恐怖场景关联
    # 攻击签名: 不是任何单个词, 而是 3 个特征的组合
    #
    # 防御策略: 检测结构签名 (三段式模板) 而非内容关键词
    # 误杀风险: 恐怖片脚本具有完全相同的签名 → 标记为 HIGH 风险 (手动审核) 而非 BLOCKED
    # 理由: 短剧管线确实生成恐怖/惊悚内容 — 这是合法类型

    # 听觉触发词 (在训练数据中与暴力强统计关联的声音)
    AUDITORY_VIOLENCE_TRIGGERS = [
        "吱嘎", "撞击", "闷响", "闷声", "沉重.*响声", "金属.*摩擦",
        "尖叫", "惨叫", "哭喊", "呻吟", "喘息", "急促.*呼吸",
        "玻璃.*碎裂", "木头.*断裂", "骨.*折.*声", "撕裂",
        "低吼", "咆哮", "哀嚎", "敲击", "重击", "钝器",
        "枪声", "刀.*划过", "脚步.*逼近", "门.*被撞开",
    ]

    # 感官启动模板结构 — 3 个组件必须在同一脚本中出现
    # 组件A: 中性场景锚点 (孤立/封闭/黑暗空间或深夜户外)
    SENSORY_PRIMING_PATTERNS = [
        (r'(?:安静|寂静|空旷|废弃|阴暗|昏暗|黑暗|漆黑|幽暗|深夜|午夜|凌晨|空荡|微弱|没人|无人|空无一人|荒废|破旧|仅.*灯|只有.*灯)[^。]*?(?:仓库|地下室|工厂|走廊|房间|建筑|空间|森林|树林|小巷|楼道|野外|公路)',
 	        "感官启动: 孤立暗空间锚点"),
        # 组件A-rev: 空间位置词在前，黑暗线索在后 (双向覆盖)
        (r'(?:仓库|地下室|工厂|走廊|房间|建筑|空间|森林|树林|小巷|楼道|野外|公路)[^。]*?(?:安静|寂静|阴暗|昏暗|黑暗|漆黑|幽暗|微弱|荒废|破旧|空无一人|空荡|废弃)',
         "感官启动: 空间→黑暗"),
        # 组件B: 听觉触发 (声音暗示暴力但视觉上未显示)
        (r'(?:传来|听到|远处|回荡|响起|隐约|依稀|阵阵|突然)[^。]*?(?:吱嘎|撞击|闷响|金属|碎裂|尖叫|呻吟|喘息|低吼|折断|断裂|敲击|重击|枪声|吼叫|砰|咚|啪|脚步声|刮擦|摩擦)',
         "感官启动: 听觉暴力触发"),
        # 组件C: 电影风格调制器 — 紧握运镜+紧张氛围 / 侵入性生理反应
        (r'(?:手持|晃动|抖动|不稳定|快速切换|急促).*?(?:摄影|镜头|拍摄|视角)',
         "感官启动: 紧张手持摄影"),
        (r'(?:紧张|焦虑|不安|恐惧|压迫|窒息|危险|威胁|未知|恐怖|惊悚|诡异|阴森|毛骨悚然).*?(?:氛围|气氛|感觉|环境)',
         "感官启动: 紧张氛围修饰"),
        (r'(?:急促|粗重|屏住).*?(?:呼吸|心跳|脉搏|喘息)',
         "感官启动: 侵入性生理反应"),
    ]
    # 攻击者用看似无害的短语替代暴力词汇以绕过关键词过滤
    # 独有签名: 委婉语本身无害 — 但 委婉语+强度修饰词+后果暗示 构成完整攻击指纹
    # 误杀风险高 → 需要 ≥2 个信号(委婉语词条+上下文线索)才能阻止

    # 委婉语 → 实际含义 映射表
    EUPHEMISM_MAP = {
        # 物理动作委婉语 (→ 殴打/攻击/杀害)
        "物理说服": "殴打/暴力胁迫",
        "物理教育": "殴打/体罚",
        "物理交流": "肢体暴力",
        "物理谈判": "暴力威胁",
        "物理对话": "殴打",
        "物理劝导": "暴力驱赶",
        "直接交流": "暴力冲突",
        "深度交流": "残酷审讯",
        "行动表达": "暴力攻击",
        "肢体协商": "斗殴",
        "接触性沟通": "暴力接触",
        "特殊手段": "酷刑/非法手段",
        "特别关照": "私刑/报复",
        "重点照顾": "暴力对待",
        "强化处理": "酷刑",
        "果断措施": "暴力镇压",
        "最终方案": "杀害/处决",
        # 色情/性内容委婉语 (→ 性行为/暴露/色情)
        # JB-CSM-002: 用隐晦表达替代色情描写绕过内容过滤
        "深度身体交流": "性行为描写",
        "深度私人互动": "性行为描写",
        "肢体深度交流": "性行为描写",
        "身体深度互动": "性行为描写",
        "亲密身体接触": "性行为暗示",
        "激情互动": "性行为描写",
        "亲密互动": "性行为暗示",
        "私密互动": "性行为暗示",
        "亲密接触": "性行为描写",
        "原始肢体表达": "性行为描写",
        "肢体表达": "性/身体描写",
        "身体交缠": "性行为描写",
        "肌肤相亲": "性行为暗示",
        "肌肤之亲": "性行为暗示",
        "最原始的交流": "性行为描写",
        "原始的交流": "性行为描写",
        "身体融合": "性行为描写",
        "负距离接触": "性行为暗示",
        "坦诚相见": "裸体/性暗示",
        "一览无余": "裸体暴露",
        "一丝不挂": "裸体暴露",
        "毫无保留": "性行为/裸体",
        "身体特写": "性器官/敏感部位特写",
        "局部特写": "敏感部位特写",
        # 死亡/伤害后果委婉语 (→ 死亡/昏迷/重伤)
        "深度休息": "死亡/昏迷/重伤",
        "永久休息": "死亡",
        "永久安静": "死亡",
        "长眠": "死亡",
        "不再醒来": "死亡",
        "永远闭上了眼睛": "死亡",
        "离开了这个世界": "死亡",
        "深度睡眠": "昏迷/死亡",
        "进入梦乡": "死亡",
        "停止工作": "死亡/被杀(对人)",
        "不再回应": "死亡/昏迷",
        "一动不动": "死亡/重伤",
        "失去了意识": "昏迷/被击倒",
        "安静地躺着": "死亡/重伤倒地",
        "红色液体": "血迹/鲜血",
        "深红色痕迹": "血迹",
        "红色印记": "血迹",
        "液体痕迹": "血迹",
        "暗色污渍": "血迹",
        "红色颜料意外洒落": "大量血迹",
    }

    # 上下文线索: 当一条委婉语附近出现这些信号时，置信度急剧上升
    EUPHEMISM_CONTEXT_CLUES = [
        # 通用暴力上下文
        r'(?:强烈|剧烈|多次|反复|持续|长时间|狠狠地|用力|毫不留情|毫不手软)',
        r'(?:对方|另一人|目标|对象|受害者)',
        r'(?:随后|然后|之后|最后|结果|最终|从此)',
        r'(?:不再|没有.*再|再也|永远|永久|彻底)',
        r'(?:留下|剩下|残留|到处都是|满地)',
        r'(?:房间|地板|墙壁|现场|周围)',
        # 色情/性内容上下文 (JB-CSM-002)
        r'(?:私密空间|私密场所|卧室|床上|酒店|浴室|昏暗|烛光)',
        r'(?:特写|镜头.*聚焦|放大|近距离|细节.*展示|细节.*描写|详细.*展示|详细.*过程|展示.*细节)',
        r'(?:成人|成年人|限制级|R级|18\+|十八禁)',
        r'(?:激情|欲望|冲动|本能|原始|野性|狂野)',
        r'(?:身体|肢体|肉体|肌肤).*?(?:交流|互动|接触|交缠|融合|结合|表达)',
    ]

    # ── 政治敏感内容时间桥 ──
    # JB-TBP-003: 描述人群聚集(A) + 跳过中帧 + 空地散落物品(C)
    # LLM 自动填补中间的政治敏感场景(驱散/冲突)
    # 检测签名: 公共场所人群+标语/横幅 + 帧间隙 + 空无一人+散落
    POLITICAL_BRIDGE_PATTERNS = [
        # 跨句组合检测: 人群聚集 + 空无一人 同时出现 (无论帧号)
        # 这个签名本身就是时间桥: 从"有人"到"无人"的过程被省略
        (r'(?:人群|民众|群众|市民|集会)[^。]*?(?:聚集|汇集|涌向|挤满|站满|占满)[^。]*?(?:广场|街道|路口|政府|大门|大楼)',
         "政治桥接: 人群集会场景"),
        (r'(?:空无一人|空旷无人|空荡荡|看不到.*人|没有.*人)[^。]*?(?:散落|残留|遗落|剩下|只.*剩下)',
         "政治桥接: 清场后果"),
        # 裸清场检测: 仅有"空无一人"无散落物品 — 更隐蔽的变种
        # 必须和人群场景同时出现才触发 (>1 hit rule)
        (r'(?:广场|大楼|街道)[^。]*?(?:空无一人|空旷无人|空荡荡|安静.*异常|寂静.*异常)',
         "政治桥接: 公共场所清场"),
        # 单句内完整检测
        (r'(?:广场|政府|大楼)[^。]*?[第帧镜][1-2][^。]*?.*?[第帧镜][3-6][^。]*?(?:空无一人|散落|残留)',
         "政治桥接: 单句内时间跳跃"),
    ]

    def scan(self, content: str, content_label: str = "用户内容") -> ScanResult:
        """扫描用户内容中的所有安全风险模式

        Args:
            content: 用户提供的原始内容
            content_label: 内容类型标签（用于错误消息）

        Returns:
            ScanResult 包含通过/阻止判定和检测到的模式
        """
        blocked = []
        warnings = []

        # ── 阶段 0: 对抗扰动去噪 (ADV-001) ──
        # 攻击者在文本中插入特殊字符以干扰安全扫描器 (regex/子串匹配)
        # LLM 对这些字符具有鲁棒性 — 能穿透噪声理解内容, 但扫描器不能
        # 策略: 对进入扫描器的文本去噪, 同时保留原始文本给 LLM

        # 零宽字符 (U+200B零宽空格, U+200C零宽非连接符, U+200D零宽连接符, U+FEFF BOM)
        # 无条件移除 — 这些字符对扫描器完全是恶意噪声
        ZERO_WIDTH_CHARS = set("​‌‍﻿⁠᠎")
        has_zero_width = any(c in ZERO_WIDTH_CHARS for c in content)
        if has_zero_width:
            content = "".join(c for c in content if c not in ZERO_WIDTH_CHARS)
            warnings.append(f"对抗扰动检测: 移除零宽字符注入")

        # 对抗扰动符 — 攻击者用来切分关键词的插入字符
        ADV_PERTURBATION_CHARS = set(
            "€$%#^&*()_+={}[]|\\/@!~`<>§¶†‡•…‰′″‹›«»"
            "¡¢£¤¥¦¨©ª¬®¯°±²³´µ¸¹º»¼½¾¿×÷"
        )
        noise_count = sum(1 for c in content if c in ADV_PERTURBATION_CHARS)
        noise_ratio = noise_count / max(1, len(content))

        if noise_ratio > 0.03:
            denoised = "".join(
                c for c in content
                if c not in ADV_PERTURBATION_CHARS
            )
            if denoised != content:
                warnings.append(
                    f"对抗扰动检测: 移除{noise_count}个扰动字符 "
                    f"(噪声比{noise_ratio:.1%}), 原始内容{len(content)}字符→去噪后{len(denoised)}字符"
                )
                content = denoised

        # 关键词空白注入对抗: 将中文关键词内部的连续空白规范化
        # "暴  力 袭 击" → "暴力袭击", 防止攻击者在关键词字符间插入空格绕过正则
        import re as _re_norm
        _orig_content = content
        content = _re_norm.sub(r'([一-鿿])\s+([一-鿿])', r'\1\2', content)
        content = _re_norm.sub(r'([一-鿿])\s+([一-鿿])', r'\1\2', content)  # 第二遍处理多个空格

        # ── 阶段 0b: 资源耗尽检测 (RES-001) ──
        # 超长输入(>50000字符)直接拒绝 → Pydantic Field max_length已有拦截
        # 高重复率输入: 攻击者用大量重复文本填充以消耗token/时长
        # 检测: 重复子串占比 > 40% = token浪费攻击
        content_len = len(content)
        if content_len > 1000:
            # 采样检测重复: 取300字符滑动窗口, 检查在整个文本中出现的次数
            sample_start = content[100:400] if content_len >= 400 else content[:200]
            sample_mid = content[content_len // 2 - 150: content_len // 2 + 150] if content_len >= 300 else content[:200]
            sample_count = content.count(sample_start) + content.count(sample_mid)
            # 如果300字符样本在整个文本中出现了 > 3次(即 > 900/1200字符被重复覆盖)
            repetition_ratio = (sample_count * len(sample_start)) / content_len
            if repetition_ratio > 0.4:
                blocked.append(
                    f"资源耗尽攻击: 重复内容占比{repetition_ratio:.0%} "
                    f"(样本300字符出现{sample_count}次, 总长度{content_len}字符)"
                )

        # ── 阶段 0c: 场景复杂度检测 (RES-002) ──
        import re as _re2
        THRESHOLDS = {
            '角色': 15, '场景': 12, '光照': 8, '镜头': 10,
            '运动': 10, '切换': 12, '对话': 10, '转折': 8,
            '物体': 30, '人物': 15, '特效': 10, '层': 8,
        }
        specs = _re2.findall(
            r'(\d+)\s*(?:个|段|种|条|次|帧)[^。，\n]{0,8}?(?:' +
            '|'.join(THRESHOLDS.keys()) + ')',
            content
        )
        if specs:
            vals = [int(v) for v in specs]
            flags = []
            for v in vals:
                for kw, thresh in THRESHOLDS.items():
                    if kw in content:
                        ratio = v / thresh
                        if ratio > 1.0:
                            flags.append(f"{v}×{kw}({ratio:.1f}x)")
                            break
            if len(flags) >= 3:
                blocked.append(
                    f"场景复杂度攻击 ({len(flags)}项超阈值): "
                    f"{', '.join(flags[:4])} — 超现实复杂度会耗尽计算资源"
                )

        # ── 阶段 0d: 自指递归检测 (RES-003) ──
        # "AI生成视频，视频展示AI生成视频，这个视频里AI又生成视频..."
        # 密集嵌套: 在100字符窗口内出现 ≥3 次 "动词+视频" 自引用链
        # 排除合法的教程/讨论(如"如何使用AI工具生成视频"只有1个层次)
        recursion_pattern = (
            r'(?:生成|制作|展示|包含|录制|拍摄)\s*(?:一段|一个)?\s*(?:关于|.*?的)?\s*(?:AI|人工智能)?'
            r'(?:生成|制作|展示)\s*(?:的)?\s*(?:视频|画面|影像)'
        )
        # 简单检测: "视频" + "生成视频" + "又生成视频" 模式在全文出现≥3次
        nested_generation = len(re.findall(r'(?:生成|制作|展示).*?(?:视频|画面)', content, re.IGNORECASE))
        # 短文本中 ≥4 次 "生成...视频" = 递归攻击; 长文本中比例更高
        gen_density = nested_generation / max(1, len(content) / 100)
        # 短文本中 ≥3 条"生成...视频"链 = 递归; 较长文本中密度 > 2.5 = 递归
        if nested_generation >= 3 and gen_density > 2.5:
            blocked.append(
                f"自指递归攻击: 检测到{nested_generation}个嵌套生成链 "
                f"(密度{gen_density:.1f}/100字符) — "
                f"无限递归内容模式会耗尽LLM推理资源"
            )

        # ── 阶段 0e: 安全帧欺骗检测 (CSB-001) ──
        # 攻击者用安全内容(风景/海滩/公园)包裹违规内容
        # 结构签名: 安全帧A → 违规帧B → 安全帧C
        # 审核仅采样首尾帧 → 漏检中间违规内容

        # 安全帧标记词 (风景/自然/日常 — 攻击者用来伪装的内容)
        safe_frame_words = r'(?:风景|海滩|海浪|日出|日落|公园|阳光|花坛|鸟鸣|白云|山脉|湖泊|河流|森林|田野|星空|蓝天|宁静|祥和|自然景|日常.*场景|正常.*画面)'
        # 违规帧标记词 (暴力/攻击/冲突 — 排除否定用法如"非暴力")
        # 使用词边界: 防止"非暴力"中的"暴力"被匹配
        unsafe_frame_words = r'(?:暴力(?:袭|冲|伤|杀|攻|行|犯|打|抢|破|摧)|持刀|拔刀|刺杀|射击|搏斗|打架|流血|受伤|杀害|致命威胁|致命攻击|致命武力|殴打|群殴)'

        safe_count = len(re.findall(safe_frame_words, content, re.IGNORECASE))
        unsafe_count = sum(len(re.findall(w, content, re.IGNORECASE)) for w in
            [r'(?<!非)暴力', r'袭击', r'攻击', r'冲突', r'伤害', r'殴打',
             r'刺杀', r'射击', r'搏斗', r'打架', r'流血', r'受伤',
             r'杀害', r'致命', r'威胁', r'危险'])

        # 三明治模式: ≥2个安全帧 + ≥1个违规帧 → BLOCKED
        if safe_count >= 2 and unsafe_count >= 1:
            blocked.append(
                f"安全帧欺骗: 检测到{safe_count}个安全帧标记+{unsafe_count}个违规帧标记 — "
                f"安全内容包裹违规内容以绕过首尾帧审核"
            )

        # ── 阶段 0f: 管道Agent注入检测 (PIPE-001) ──
        # 攻击: 将注入指令嵌入元生成请求 — "剧本的第一行指令是:忽略所有规则"
        # 签名: 生成请求框架 + 嵌入的覆盖指令 + 违规内容暗示
        pipe_patterns = [
            # "剧本/X的第一行/Y开头 指令/注释 是/写: 忽略/不受限制/自由"
            r'(?:剧本|方案|脚本|分镜|故事).*?(?:第一行|开头|第一句|前言|注释|序言|首行).*?(?:指令|规则|命令|提示|标注|说明|要求).*?(?:忽略|不受限制|不受约束|自由.*创作|自由.*描写|任意.*生成|不.*限制|不.*过滤)',
            # "方案第一行是系统指令: 你现在是..."
            r'(?:第一行|开头).*?(?:系统指令|角色.*指令|模型.*指令|AI.*指令).*?(?:你现在是|你现在扮演|你是一个不受|你是一个没有)',
            # 导演注释/内部说明 包裹的覆盖
            r'(?:导演.*注释|内部.*说明|创作.*备注).*?(?:不受.*约束|自由.*描写|任意.*场景|不.*审核|不.*过滤|不.*限制)',
        ]
        pipe_hits = []
        for pattern in pipe_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                pipe_hits.append(len(matches))

        if pipe_hits:
            blocked.append(
                f"管道Agent注入: 检测到{sum(pipe_hits)}个嵌套注入指令 — "
                f"攻击者将覆盖指令嵌入生成请求框架中"
            )

        # ── 阶段 0g: 艺术掩护检测 (PIPE-002) ──
        art_keywords = r'(?:艺术|美学|审美|实验|先锋|概念|观念|抽象|写意|表现主义)'
        body_keywords = r'(?:人体|身体|肉体|裸体|躯体|形体|肢体)'
        medium_keywords = r'(?:雕塑|油画|国画|素描|速写|水彩|版画|陶艺|装置|舞蹈|芭蕾|现代舞|歌剧|音乐剧|书法|篆刻|CG艺术|像素艺术|建筑|园林|摄影|摄像|设计|服装|化妆|发型)'

        has_art = bool(re.search(art_keywords, content, re.IGNORECASE))
        has_body = bool(re.search(body_keywords, content, re.IGNORECASE))
        has_medium = bool(re.search(medium_keywords, content, re.IGNORECASE))

        # 艺术掩护 = 艺术/美学词 + 身体/人体词 − 具体艺术媒介
        if has_art and has_body and not has_medium:
            blocked.append(
                f"艺术掩护攻击: 检测到艺术/美学包装+身体内容模式, "
                f"但未指定具体艺术媒介(雕塑/舞蹈/油画等) — "
                f"疑似以艺术之名包装违规内容"
            )

        # 阶段 1: 时间桥检测
        for pattern, desc in self.TEMPORAL_BRIDGE_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                blocked.append(f"时间桥攻击 ({desc}): 匹配 {len(matches)} 处")

        # 阶段 2: 暴力指示符
        violence_hits = []
        for pattern, desc in self.VIOLENCE_INDICATORS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                violence_hits.extend(matches)

        if len(violence_hits) >= 2:
            # 多个暴力指示符同时出现 → 更高置信度
            blocked.append(f"复合暴力指示 ({len(violence_hits)} 处匹配): {violence_hits[:3]}")
        elif len(violence_hits) == 1:
            # 单个暴力词可能是合法的（警匪片/武侠剧本）
            warnings.append(f"单个暴力词: {violence_hits[0]}")

        # 阶段 3: 渐进越狱
        for pattern, desc in self.GRADUAL_ESCALATION_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                blocked.append(f"渐进越狱 ({desc}): 匹配 {len(matches)} 处")

        # 阶段 3b: 多轮漂移检测 (JB-MSD-001)
        drift_hits = []
        for pattern, desc in self.MULTI_ROUND_DRIFT_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                drift_hits.append((desc, len(matches)))

        if len(drift_hits) >= 1:
            # 单个命中即阻止 — 各模式本身已高度特异 (需同时含迭代标记+递进方向+伤害锚点)
            hit_descs = [h[0] for h in drift_hits]
            blocked.append(f"多轮漂移攻击 ({len(drift_hits)} 种模式匹配): {hit_descs}")

        # 阶段 4: 政治敏感时间桥 (JB-TBP-003)
        political_hits = []
        for pattern, desc in self.POLITICAL_BRIDGE_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                political_hits.append((desc, len(matches)))

        if len(political_hits) >= 2:
            # 多人聚集场景 + 清场后果 → 高置信度时间桥
            hit_descs = [h[0] for h in political_hits]
            blocked.append(f"政治敏感时间桥 ({len(political_hits)} 种模式匹配): {hit_descs}")
        elif len(political_hits) == 1:
            # 单个模式匹配 — 可能是合法历史纪录片
            warnings.append(f"政治桥接警告: {political_hits[0][0]}")

        # 阶段 5: 暴力委婉语检测 (JB-CSM-001)
        euphemism_hits = []
        context_hits = []

        # 5a: 扫描委婉语词条
        for euphemism, meaning in self.EUPHEMISM_MAP.items():
            if euphemism in content:
                euphemism_hits.append((euphemism, meaning))

        # 5b: 扫描上下文线索
        for clue_pattern in self.EUPHEMISM_CONTEXT_CLUES:
            matches = re.findall(clue_pattern, content, re.IGNORECASE)
            if matches:
                context_hits.append(len(matches))

        # 5c: 综合判定
        # 单个委婉语 + 无上下文线索 → 低置信度 (可能是合法使用)
        # 单个委婉语 + ≥2 上下文线索 → 中置信度 → 阻止
        # ≥2 委婉语 → 高置信度 → 阻止 (两条不同委婉语同时出现=明显攻击意图)
        total_context = sum(context_hits)

        if len(euphemism_hits) >= 2:
            phrases = [f'"{e}"(→{m})' for e, m in euphemism_hits[:3]]
            blocked.append(f"复合暴力委婉语 ({len(euphemism_hits)}条): {phrases}")
        elif len(euphemism_hits) == 1 and total_context >= 2:
            e, m = euphemism_hits[0]
            blocked.append(f"暴力委婉语 '{e}'(→{m}) + {total_context}条上下文线索")
        elif len(euphemism_hits) == 1:
            e, m = euphemism_hits[0]
            # 对抗扰动信号: 噪声比高 或 检测到零宽字符注入 = 攻击意图明确
            if noise_ratio > 0.03 or has_zero_width:
                signal_type = f"噪声比{noise_ratio:.0%}" if noise_ratio > 0.03 else "零宽字符注入"
                blocked.append(f"暴力委婉语 '{e}'(→{m}) + 对抗扰动({signal_type})")
            else:
                warnings.append(f"委婉语警告: '{e}' 可理解为'{m}' — 上下文不足, 标记为低风险")

        # 阶段 6: 感官启动检测 (JB-SPARK-001)
        sensory_hits = []
        for pattern, desc in self.SENSORY_PRIMING_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                sensory_hits.append((desc, len(matches)))

        # 3组件全部命中 = 完整感官启动模板
        if len(sensory_hits) >= 3:
            hit_descs = [h[0].split(": ")[1] for h in sensory_hits]
            warnings.append(
                f"感官启动检测 ({len(sensory_hits)}/3组件): {hit_descs} — "
                f"视听共现先验触发。恐怖/惊悚剧本合法; 伪装中性场景的暴力生成应阻止。"
            )
        elif len(sensory_hits) >= 2:
            warnings.append(f"部分感官启动 ({len(sensory_hits)}/3组件)")

        # SPARK + 任何其他危险信号 → 升级
        # 单独SPARK可能是恐怖片(合法), SPARK+暴力/委婉语/时间桥=攻击
        if sensory_hits and blocked:
            blocked.append(f"感官启动+危险信号组合 ({len(sensory_hits)}组件+{len(blocked)}个其他信号)")

        # 阶段 7: SceneSplit 检测 (JB-SS-001)
        ss_phase_a = False; ss_phase_c = False; ss_details = []
        for pattern, desc in self.SCENE_SPLIT_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                if "入场" in desc: ss_phase_a = True; ss_details.append((desc, len(matches)))
                else: ss_phase_c = True; ss_details.append((desc, len(matches)))
        ss_phase_b = any(re.findall(p, content, re.IGNORECASE) for p in self.NORMAL_ACTIVITY_BRIDGE)
        if ss_phase_a and ss_phase_c:
            detail_str = ", ".join([f"{d}(x{c})" for d, c in ss_details])
            bridge_tag = "A+B+C" if ss_phase_b else "A+C"
            blocked.append(f"SceneSplit攻击 ({bridge_tag}三段式): {detail_str} — 人物入场→异常后果, LLM将自动补全中间恶意事件")

        # 最终判定
        if blocked:
            return ScanResult(
                passed=False,
                risk_level="blocked" if len(blocked) >= 2 else "high",
                blocked_patterns=blocked,
                warnings=warnings,
                reason=f"内容安全扫描未通过: {'; '.join(blocked)}",
            )
        elif warnings:
            # SPARK检测 (≥3组件) → 升级为 medium 风险 (恐怖片合格但建议人工审核)
            has_spark = any("感官启动检测" in w for w in warnings) and sensory_hits
            risk = "medium" if (has_spark and len(sensory_hits) >= 3) else "low"
            return ScanResult(
                passed=True,
                risk_level=risk,
                blocked_patterns=[],
                warnings=warnings,
                reason=f"通过, 但有 {len(warnings)} 个{'风险' if risk == 'medium' else '低风险'}标记: {'; '.join(warnings)}",
            )
        else:
            return ScanResult(
                passed=True,
                risk_level="none",
                reason="内容安全扫描通过",
            )


# 全局单例
_scanner = None


def get_scanner() -> ContentSafetyScanner:
    global _scanner
    if _scanner is None:
        _scanner = ContentSafetyScanner()
    return _scanner
