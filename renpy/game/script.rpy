# 游戏名称：待定义
# 类型：文字冒险/视觉小说
# 平台：iOS

# ============================================
# 游戏初始化配置
# ============================================

init python:
    # 游戏配置
    config.name = "Zein Game"
    config.version = "0.1.0"
    config.save_directory = "ZeinGame"
    
    # 屏幕比例（适配 iOS）
    config.screen_width = 1280
    config.screen_height = 720
    
    # 默认属性
    default player_name = ""
    
    # 玩家属性系统
    default player_stats = {
        'strength': 0,    # 力量
        'intelligence': 0, # 智力
        'charm': 0,       # 魅力
        'luck': 0,        # 幸运
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
    python:
        player_name = renpy.input("请输入你的名字：", length=20).strip()
        if not player_name:
            player_name = "主角"
    
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

# ============================================
# 示例角色
# ============================================

define e = Character("？？？")

label example_scene:
    scene bg room
    with fade
    
    show eileen happy at center
    with dissolve
    
    e "欢迎来到这个世界！"
    
    menu:
        "你回应道：":
            "你好！":
                $ player_stats['charm'] += 1
                e "真是个友好的人呢！"
                "魅力 +1"
                
            "你是谁？":
                e "我是这个世界的引导者。"
                
            "（保持沉默）":
                e "看来你还很警惕呢。"
    
    return
