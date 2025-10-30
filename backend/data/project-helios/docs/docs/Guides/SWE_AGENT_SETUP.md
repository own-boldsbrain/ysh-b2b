# SWE-agent setup for Project Helios

This repository includes a minimal `swe.yaml` so you can run SWE-agent-like workflows locally without installing the full package from PyPI.

If you want to install the real SWE-agent, try one of the following approaches:

1. Install from GitHub (if the project is hosted on GitHub):

```powershell
# from the project root, with the virtualenv activated
C:/Users/fjuni/ysh-b2b/backend/data/project-helios/.venv/Scripts/python.exe -m pip install "git+https://github.com/SWE-agent/SWE-agent.git@main#egg=swe_agent"
```

2. If the package is available on PyPI under a different name, substitute accordingly.

3. If you prefer not to install, you can use the `swe.yaml` with a local runner that executes the commands (see `runners.default` in `swe.yaml`).

Notes and next steps:
- The configuration sets `allow_network: false` to avoid unexpected network access.
- Review `swe.yaml` and change `agent.model` to the LLM you want to use (or a local model runner).
- If you plan to allow git pushes or other destructive actions, set `safety.allow_git_push` to `true` only after reviewing the policy.

Troubleshooting:
- If pip fails with "No matching distribution", install from the GitHub repo as above.
- On Windows, ensure your virtualenv is activated before running pip.

If you want, I can attempt to install from the GitHub repo next. Do you want me to try that?