# AitoCoder CLI - REPL

## Intro
A new fork of AitoCoder / auto-coder, featuring UI redesign and various optimizations.  
新的分支，目标是重新设计交互，逐步优化使用体验，提升性能。

Use astral/uv for build & development.  
使用 uv 作为开发与发布的工具。

CODEBASE_ANALYSIS.md is a breakdown of the workflow by Opus4.5.  
仅供参考。

pyproject.toml is the standard file for project information.  
项目信息以 pyproject.toml 为准，requirement.txt 仅做参考用，不参与打包或其他任何过程。

## Dec.19 Update
@maxwellzzhou
1. 以 uv 体系重新规划开发/发布流程。
2. 重构了 LLM streamline 机制，实现 Ctrl+C 迅速停止任务。
3. 开始重新设计主界面，逐步推进终端元素统一。
4. 重新简化设计了登陆组件，删除了重复和冗余的部分。
5. 现已通过 uv publish 在 PyPI 上发布 aitocoder，可以通过 `pip install aitocoder` 安装。  
（推荐使用 `uv tool install aitocoder` / `pipx install aitocoder`）
