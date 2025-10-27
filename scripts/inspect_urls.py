import importlib, traceback

try:
    m = importlib.import_module('school_manager_project.urls')
    print('has_api =', getattr(m, 'has_api', None))
    router = getattr(m, 'router', None)
    print('router set:', bool(router))
    if router is not None:
        print('registered prefixes:', [r.prefix for r in router.registry])
except Exception:
    traceback.print_exc()
