## 游戏 UI 屏幕定义

# 主菜单
screen main_menu():
    tag menu
    
    add gui.main_menu_bg
    
    vbox:
        style_prefix "main_menu"
        xalign 0.5
        yalign 0.5
        spacing 20
        
        textbutton "开始游戏" action Start()
        textbutton "读取存档" action ShowMenu("load")
        textbutton "设置" action ShowMenu("preferences")
        textbutton "关于" action ShowMenu("about")
        textbutton "退出" action Quit(confirm=False)

# 设置界面
screen preferences():
    tag menu
    
    vbox:
        style_prefix "preferences"
        xalign 0.5
        yalign 0.5
        
        hbox:
            xalign 0.5
            spacing gui.pref_spacing
            
            textbutton "自动前进":
                action Preference("auto-forward", "toggle")
                selected Preference("auto-forward", "check")
                
            textbutton "跳过已读":
                action Preference("skip", "toggle")
                selected Preference("skip", "check")
                
        hbox:
            xalign 0.5
            spacing gui.pref_spacing
            
            textbutton "文字速度":
                action Preference("text speed", "slow")
                selected Preference("text speed", "check", "slow")
                
            textbutton "正常":
                action Preference("text speed", "normal")
                selected Preference("text speed", "check", "normal")
                
            textbutton "快速":
                action Preference("text speed", "fast")
                selected Preference("text speed", "check", "fast")
        
        textbutton "返回" action ShowMenu("main_menu")

# 存档界面
screen save():
    tag menu
    
    vbox:
        style_prefix "save"
        xalign 0.5
        yalign 0.5
        
        grid 3 2:
            spacing 10
            
            for i in range(6):
                textbutton "存档 {}".format(i+1):
                    action FileAction(i+1)
                    
        textbutton "返回" action ShowMenu("main_menu")

# 读取界面
screen load():
    tag menu
    
    vbox:
        style_prefix "load"
        xalign 0.5
        yalign 0.5
        
        grid 3 2:
            spacing 10
            
            for i in range(6):
                textbutton "读取 {}".format(i+1):
                    action FileLoad(i+1)
                    
        textbutton "返回" action ShowMenu("main_menu")

# 关于界面
screen about():
    tag menu
    
    vbox:
        style_prefix "about"
        xalign 0.5
        yalign 0.5
        spacing 20
        
        label "Zein Game"
        label "版本：0.1.0"
        label "类型：文字冒险/视觉小说"
        label "平台：iOS"
        label ""
        label "开发者：正鑫"
        label "AI 助手：zein"
        
        textbutton "返回" action ShowMenu("main_menu")
