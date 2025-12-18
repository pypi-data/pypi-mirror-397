# sshow

`sshow` 是一个用来 **美化展示 `~/.ssh/config`** 的小工具。  
它支持按注释分组、子分组展示 SSH 主机，并提供简单的搜索与高亮功能，让你的 SSH 配置一目了然。

- 支持 **Windows PowerShell / macOS Terminal / Linux 各种终端**
- 默认读取 `~/.ssh/config`（Windows 下是 `C:\Users\<用户名>\.ssh\config`）
- 终端支持 ANSI 颜色时，会自动带颜色输出

---

## 安装

```bash
pip install --break-system-packages sshow


echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
# Or
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

```

## 基本用法


```bash
sshow  # 以分组、每行2个的方式打印你的ssh config
sshow -h  # 打印所有可用命令
sshow --help
sshow -c 5  # 以分组、每行5个的方式打印你的ssh config
sshow --col 5
sshow -f path/to/your/ssh/config  # 以分组、每行2个的方式打印你指定的ssh config
sshow --file path/to/your/ssh/config
sshow -s 192  # 打印出所有包含字符串 '192' 的主机
sshow --search 192

sshow -s 192 -c 5  # 也可以组合命令
```

## 示例：

```text
#### Home
Host first
  HostName 192.168.31.20
  User Administrator

### Rasperries
Host pi8g
  HostName 192.168.31.2
  User root

Host pi4g
  HostName 192.168.31.21
  User erichuanp
```
在 `sshow` 里，结构会变成：
- 大组：`Home`
  - hosts：`first`
  - 小组：`Rasperries`
    - hosts：`pi8g`, `pi4g`

```bash
SSH Show
------------------------

Home          # 大组（来自 #### Home），以红色标识出
Host: ...
Username: ...
IP&Port: ...

Rasperries            # 小组（来自 ### Rasperries），以亮红色标识出
Host: ...
...
------------------------
```