try:
    VERSION = __import__("pkg_resources").get_distribution("odfuzz").version
except Exception:
    VERSION = "unknown"

__version__ = VERSION
