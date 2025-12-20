SHELL := /bin/bash

ARAGO_ENV ?= /opt/arago-2023.10/environment-setup
SYSROOT   ?= /opt/arago-2023.10/sysroots/aarch64-oe-linux
CC        ?= aarch64-oe-linux-gcc
PKG_CONFIG ?= pkg-config

CFLAGS   ?=
CPPFLAGS ?=
LDFLAGS  ?=
LDLIBS   ?=

export CC
export CPPFLAGS
export CFLAGS
export LDFLAGS
export LDLIBS

DIRNAME  := $(notdir $(CURDIR))
SRC_DIR  := $(CURDIR)/../..
BUILD_DIR := $(SRC_DIR)/build
SOURCES  := $(wildcard $(SRC_DIR)/*.c)
BINS     := $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%,$(SOURCES))

.ONESHELL:
.DEFAULT_GOAL := all
.PHONY: all clean build

all: $(BINS)

build: clean all

$(BUILD_DIR)/%: $(SRC_DIR)/%.c
	@mkdir -p $(BUILD_DIR)
	@echo "Compiling: $< -> $@"
	@if [ -f "$(ARAGO_ENV)" ]; then \
		source "$(ARAGO_ENV)"; \
	else \
		echo "Missing toolchain setup: $(ARAGO_ENV)" >&2; \
		exit 1; \
	fi
	$${CC:-cc} $$CPPFLAGS $$CFLAGS -o "$@" "$<" $$LDFLAGS $$LDLIBS
	@echo "Done: $@"

clean:
	$(RM) $(BINS)
