@echo off
chcp 65001 >nul
title 茶叶冲泡定时提醒程序

echo.
echo ========================================
echo    🍵 茶叶冲泡定时提醒程序 🍵
echo ========================================
echo.
echo 正在启动程序，请稍候...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未检测到Python环境
    echo.
    echo 请先安装Python 3.7或更高版本：
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 🔍 检查依赖库...
python -c "import PIL, matplotlib, numpy" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  检测到缺少依赖库，正在自动安装...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ❌ 依赖安装失败，请手动运行：
        echo pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo ✅ 依赖检查完成
echo.
echo 🚀 启动程序...
echo.

REM 启动程序
python main.py

REM 程序结束后的处理
if errorlevel 1 (
    echo.
    echo ❌ 程序运行出错
    echo.
) else (
    echo.
    echo ✅ 程序正常退出
    echo.
)

echo 感谢使用茶叶冲泡定时提醒程序！
echo.
pause