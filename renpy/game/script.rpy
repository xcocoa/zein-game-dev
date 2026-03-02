# 游戏名称：Zein Game
# 类型：文字冒险/视觉小说
# 平台：iOS

# ============================================
# 游戏初始化
# ============================================

# 默认变量
default player_name = ""

# 玩家属性系统
default player_stats = {
    'strength': 0,      # 力量
    'intelligence': 0,  # 智力
    'charm': 0,         # 魅力
    'luck': 0,          # 幸运
}

# 好感度系统
default character_affection = {}

# ============================================
# 开场
# ============================================

label start:
    scene black
    with fade
    
    "游戏开始..."
    
    # 玩家名字输入
    $ player_name = renpy.input("请输入你的名字：", length=20).strip()
    $ if not player_name: player_name = "主角"
    
    "你好，[player_name]！"
    
    "这是一个全新的冒险..."
    
    # 第一个选择支
    menu:
        "你决定：":
            "探索周围":
                $ player_stats['intelligence'] += 1
                "你仔细观察周围的环境，发现了一些线索。"
                "智力 +1"
                
            "直接前进":
                $ player_stats['strength'] += 1
                "你鼓起勇气，大步向前走去。"
                "力量 +1"
                
            "等待观察":
                $ player_stats['luck'] += 1
                "你决定先按兵不动，看看会发生什么。"
                "幸运 +1"
    
    # 继续剧情
    "你的冒险才刚刚开始..."
    
    return
