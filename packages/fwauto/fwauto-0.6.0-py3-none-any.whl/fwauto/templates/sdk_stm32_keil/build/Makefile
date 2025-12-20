# FWAuto Build Makefile - PowerShell Wrapper

# 參數設定
PROJECT_ROOT ?= ../..
KEIL_UV4 ?= C:\Keil_v5\UV4\UV4.exe

# 主要 target
.PHONY: build

build:
	@powershell -ExecutionPolicy Bypass -File build.ps1 -ProjectRoot "$(PROJECT_ROOT)" -KeilUV4 "$(KEIL_UV4)"
