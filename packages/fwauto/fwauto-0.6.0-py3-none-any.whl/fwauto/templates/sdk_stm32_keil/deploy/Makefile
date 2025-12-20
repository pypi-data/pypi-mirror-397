# FWAuto Deploy Makefile - PowerShell Wrapper

# 參數設定
PROJECT_ROOT ?= ../..
HEX_FILE ?= $(PROJECT_ROOT)/OBJ/Template.hex
STLINK_CLI ?= C:\Program Files (x86)\STMicroelectronics\STM32 ST-LINK Utility\ST-LINK Utility\ST-LINK_CLI.exe

# 主要 target
.PHONY: deploy

deploy:
	@powershell -ExecutionPolicy Bypass -File deploy.ps1 -ProjectRoot "$(PROJECT_ROOT)" -HexFile "$(HEX_FILE)" -StLinkCli "$(STLINK_CLI)"
