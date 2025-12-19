class LibraryInfo:
    version_lib = 'v1.9.11'
    name = 'pvmlib'
    author = "Henrry Cañedo"
    author_email = "henrry.canedo@coppel.com"
    description = "Python library for PVM"
    python_requires = '>=3.12'
    env = 'prod'
    
    install_requires = [
        "google-cloud-logging>=3.12.1",
        "pydantic-settings>=2.9.1",
        "pydantic>=2.11.4",
        "pytz>=2025.2",
        "circuitbreaker>=2.1.3",
        "tenacity>=9.1.2",
        "pybreaker>=1.3.0",
        "aiohttp>=3.11.18",
        "starlette>=0.49.1",
        "urllib3>=2.6.2",
        "charset_normalizer>=2.0.0,<3.0.0",
        "motor>=3.7.0",
        "colorama>=0.4.6",
    ]