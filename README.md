## GoodHealth

[![Health Report](https://github.com/jungheil/GoodHealth/actions/workflows/action.yml/badge.svg?event=schedule)](https://github.com/jungheil/GoodHealth/actions/workflows/action.yml)

东大学生每日一用，确保健康。

### 部署

1. Fork本仓库，或将该仓库上传到自己的github上。

2. 点击仓库的`Settings`，找到`Secrets`，点击`New repository secret`，新增如下两个值：

   | Name       | Value          |
   | ---------- | -------------- |
   | `USERNAME` | 你的学号       |
   | `PASSWORD` | 你的一网通密码 |

3. 将在早晨6点左右自动食用。想食用时间可自行修改`.github/workflows/action.yml`文件。

### 说明

1. 食用时间并不准确，可能会有延迟（甚至长达几个小时）。可自行使用服务器或云函数解决。
2. 本工具仅限身体健康者食用，否则后果自负。