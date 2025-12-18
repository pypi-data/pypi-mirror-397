import setuptools

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ubicoders-testpy", # Naming it testpy_package to be safe, user can change
    version="0.0.2",
    author="User",
    author_email="info@ubicoders.com",
    description="A small test base",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    py_modules=["utils_test"],
    python_requires=">=3.6",
)
