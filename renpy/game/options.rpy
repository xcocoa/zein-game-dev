## Ren'Py 游戏选项配置

## 基础设置
define config.name = "Zein Game"
define config.version = "0.1.0"
define config.save_directory = "ZeinGame"
define config.window = "show"
define config.window_show_transition = Dissolve(0.2)
define config.window_hide_transition = Dissolve(0.2)

## 屏幕尺寸（适配 iOS）
define config.screen_width = 1280
define config.screen_height = 720

## 默认过渡效果
define config.default_transition = Dissolve(0.5)
define config.default_in_transition = Dissolve(0.5)
define config.default_out_transition = Dissolve(0.5)

## 忽略未知属性
define config.ignore_errors = False

## 自动保存
define config.has_autosave = True
define config.autosave_on_quit = True
define config.autosave_slots = 5

## 日志历史
define config.history_length = 250

## 快速保存/读取
define config.quick_menu = True

## 跳过已读文本
define config.after_load_callbacks.append = SetVariable('skip_unseen', False)

## 移动端优化
define config.touch_rollback = True
define config.gl_resize_window = False
