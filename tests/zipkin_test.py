import mock

from pyramid_zipkin import zipkin


@mock.patch('pyramid_zipkin.zipkin.ZipkinLoggingContext', autospec=True)
@mock.patch('pyramid_zipkin.zipkin.create_zipkin_attr', autospec=True)
@mock.patch('pyramid_zipkin.zipkin.create_endpoint', autospec=True)
@mock.patch('pyramid_zipkin.zipkin.get_binary_annotations', autospec=True)
def test_tween_is_wrapped_by_zipkin_logging_context(
        binann_mock, endp_mock, attrs_mock, context):
    instance = context.return_value
    attrs_mock.return_value = 'zipkin_attrs'
    binann_mock.return_value = {'k': 'v'}
    endp_mock.return_value = 'endpoint_attrs'
    tween = zipkin.zipkin_tween(mock.Mock(), 'registry')
    tween(mock.Mock())
    instance.__enter__.assert_called_once_with()
    instance.__exit__.assert_called_once_with(None, None, None)


@mock.patch('pyramid_zipkin.zipkin.get_zipkin_attrs', autospec=True)
def test_create_headers_for_new_span_raises_if_no_active_request(get_mock):
    get_mock.return_value = None
    assert {} == zipkin.create_headers_for_new_span()


@mock.patch('pyramid_zipkin.zipkin.get_zipkin_attrs', autospec=True)
@mock.patch('pyramid_zipkin.zipkin.generate_span_id', autospec=True)
def test_create_headers_for_new_span_returns_header_if_active_request(
        gen_mock, get_mock):
    get_mock.return_value = mock.Mock(
        trace_id='1', span_id='3', is_sampled=True)
    gen_mock.return_value = '2'
    expected = {
        'X-B3-TraceId': '1',
        'X-B3-SpanId': '2',
        'X-B3-ParentSpanId': '3',
        'X-B3-Flags': '0',
        'X-B3-Sampled': '1',
        }
    assert expected == zipkin.create_headers_for_new_span()
