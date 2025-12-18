1. Install Python 3.11 via deadsnakes PPA (recommended for side-by-side install):
```shell
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-dev
```

2. Use python3.11 directly (do not change system default):
```shell
python3.11 -m venv myenv
source myenv/bin/activate
```

## Repairing broken Python installation

Your Python environment is broken due to mismatched system Python and manually installed versions. Here’s how to fix and get a stable Python 3.11 setup on Ubuntu 22.04 in WSL:

1. Reset Python alternatives (if you changed them):
```shell
sudo update-alternatives --remove-all python3 || true
sudo ln -sf /usr/bin/python3.10 /usr/bin/python3
```
2. Remove broken or conflicting Python 3.11 packages:
```shell
sudo apt-get remove --purge python3.11 python3.11-venv python3.11-dev python3-apt
sudo apt-get autoremove
```
3. Reinstall system Python and dependencies:
```shell
sudo apt-get update
sudo apt-get install --reinstall python3 python3-venv python3-dev python3-apt
```
4. (Optional) Install Python 3.11 via deadsnakes PPA (recommended for side-by-side install):
```shell
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-dev
```
5. Use python3.11 directly (do not change system default):
```shell
python3.11 -m venv myenv
source myenv/bin/activate
```