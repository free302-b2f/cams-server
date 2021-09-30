"""패키지 초기화
 + __all__ 정의
"""

from os.path import dirname, basename, isfile, join
import glob

modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

__all__.remove('utility')
__all__.remove( "B2F_CAMs_DashBoard_timing")
__all__.remove( "B2F_CAMs_DashBoard_Expert")
__all__.remove( "camera_viewer_old")
__all__.remove( "camera_viewer")
__all__.remove( "ws_tester")
# __all__.remove( "B2F_CAMs_DashBoard")

#__all__ = ['home', 'mongo', 'timedb', 'B2F_CAMs_DashBoard']
#__all__ = ['home']

