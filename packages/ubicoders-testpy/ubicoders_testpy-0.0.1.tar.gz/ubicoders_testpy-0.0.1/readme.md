
python -m build

unzip -l dist/*.whl

twine upload dist/*