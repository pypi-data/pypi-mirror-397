import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="chq-pybos",
    version="0.0.2",
    author="Jared Brown",
    author_email="jbrown@chq.org",
    description="A Python client library for BOS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.it.chq.org/IT/pybos",
    project_urls={"Bug Tracker": "https://gitlab.it.chq.org/IT/pybos/-/issues"},
    packages=["pybos"],
    install_requires=["requests", "xmltodict"],
)
