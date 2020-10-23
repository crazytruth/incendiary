from insanic import Insanic

from incendiary import Incendiary

from .views import (
    MockView,
    MockErrorView,
    ExceptionView,
    MockInterServiceError,
    MockInterServiceView,
)


app = Insanic("incendiary1", version="0.1.0")
Incendiary.init_app(app)

app.add_route(MockErrorView.as_view(), "/trace_error")
app.add_route(ExceptionView.as_view(), "/trace_exception")
app.add_route(MockInterServiceError.as_view(), "/trace_error_1")
app.add_route(MockView.as_view(), "/trace")
app.add_route(MockInterServiceView.as_view(), "/trace_1")
