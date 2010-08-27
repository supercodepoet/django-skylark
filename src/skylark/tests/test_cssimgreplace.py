import py.test

from nose.tools import with_setup
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest

from skylark import cssimgreplace

RAW = """
/* Common use case */
.class {
    background: white url("../images/img1.gif");
}
.class {
    background: white url('../images/img1.gif');
}
.class {
    background: white url(../images/img1.gif);
}

/* What about just an image in the same directory */
.class {
    background: white url("img1.gif");
}

/* And in the same directory, just phrased a bit differently */
.class {
    background: white url("./img1.gif");
}

/* Out a couple of directories */
.class {
    background: white url("../../../page2/images/img1.gif");
}

/* What about escaped characters */
.class {
    background: white url("../../../crazy\\\\page/images/img1.gif");
}

/* And the rest of these should not be touched */
.class {
    background: white url("http://google.com/img/logo.gif");
}
.class {
    background: white url("/cfcache/out/base/media/img/test.gif");
}
"""

EXPECTED = """
/* Common use case */
.class {
    background: white url("http://testserver/media/cfcache/out/dummyapp/page/media/images/img1.gif");
}
.class {
    background: white url('http://testserver/media/cfcache/out/dummyapp/page/media/images/img1.gif');
}
.class {
    background: white url(http://testserver/media/cfcache/out/dummyapp/page/media/images/img1.gif);
}

/* What about just an image in the same directory */
.class {
    background: white url("http://testserver/media/cfcache/out/dummyapp/page/media/css/img1.gif");
}

/* And in the same directory, just phrased a bit differently */
.class {
    background: white url("http://testserver/media/cfcache/out/dummyapp/page/media/css/img1.gif");
}

/* Out a couple of directories */
.class {
    background: white url("http://testserver/media/cfcache/out/dummyapp/page2/images/img1.gif");
}

/* What about escaped characters */
.class {
    background: white url("http://testserver/media/cfcache/out/dummyapp/crazy\\\\page/images/img1.gif");
}

/* And the rest of these should not be touched */
.class {
    background: white url("http://google.com/img/logo.gif");
}
.class {
    background: white url("/cfcache/out/base/media/img/test.gif");
}
"""

def test_will_replace_url_values():
    result = cssimgreplace.relative_replace(RAW,
        'dummyapp/page/media/css/',
        'http://testserver/media/cfcache/out/')
    assert result == EXPECTED
