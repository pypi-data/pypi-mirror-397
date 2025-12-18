from setuptools import setup, find_packages


setup(
    name="cascade-framework",
    version="1.0.0",
    description="Explicit, deterministic runtime validation framework for Python",
    author="XGCascade",
    author_email="cascade.framework@proton.me",
    python_requires=">=3.10",
    license="MIT",
    packages=find_packages(include=["cascade", "cascade.*"]),
    package_data={
        "cascade": ["py.typed"],
    },
    include_package_data=True,
)
