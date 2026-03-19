# Hello World Python Project

这是一个简单的Python Hello World项目，通过GitHub Actions自动化部署。

## 项目结构

```
hello-world/
├── main.py          # 主程序
├── requirements.txt # 依赖
├── .github/
│   └── workflows/
│       └── python.yml  # GitHub Actions工作流
└── README.md
```

## 运行方式

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

## GitHub Actions

每次推送到main分支会自动触发CI/CD流水线。
