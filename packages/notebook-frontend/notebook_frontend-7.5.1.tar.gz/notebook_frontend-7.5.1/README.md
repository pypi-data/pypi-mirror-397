# notebook-frontend

A Python package distributing Notebook's static assets only, with no Python dependency.

```bash
git clean -fdx
curl --output notebook-7.5.1-py3-none-any.whl https://files.pythonhosted.org/packages/d1/86/ca516cb58ad2cb2064124d31cf0fd8b012fca64bebeb26da2d2ddf03fc79/notebook-7.5.1-py3-none-any.whl
unzip notebook-7.5.1-py3-none-any.whl
mkdir -p share
cp -r notebook-7.5.1.data/data/share/jupyter share/
cp -r notebook/static src/notebook_frontend/
cp -r notebook/templates src/notebook_frontend/
hatch build
hatch publish
```
