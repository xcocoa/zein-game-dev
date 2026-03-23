## options.rpy - 游戏基础配置

## 游戏标题
define config.name = _("世界碎片 · World Fragments")

## 是否在主菜单显示标题和版本号
define gui.show_name = True

## 版本号
define config.version = "0.1-demo"

## 分辨率（在 gui.rpy 里统一设置为 1280x720）

## 存档
define config.has_autosave = True
define config.autosave_slots = 3

## 跳过已读文本
define config.allow_skipping = True

## 主菜单背景音乐（有音乐文件后取消注释）
# define config.main_menu_music = "audio/menu.ogg"

## 游戏内背景音乐循环
define config.fade_music = 0.5
