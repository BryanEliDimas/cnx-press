import pretend
import pytest
import requests
import requests_mock as rmock

from press.outofband import make_request

from tests.helpers import (
    count_calls,
)


class FauxMaxRetriesExceededError(BaseException):
    pass


class TestMakeRequest:

    @property
    def target(self):
        return make_request

    @pytest.fixture(autouse=True)
    def setup(self, stub_request):
        self.request = stub_request

        self.max_retries = 4

        # Mock Celery task
        @count_calls
        def retry(exc):
            if retry.call_count == self.max_retries:
                raise FauxMaxRetriesExceededError()
            self.target(self.celery_task, self.url)

        self.task_retry_method = pretend.call_recorder(retry)
        self.celery_task = pretend.stub(
            get_pyramid_request=lambda: self.request,
            retry=self.task_retry_method,
            MaxRetriesExceededError=FauxMaxRetriesExceededError,
        )

        # Define the parameters
        self.id = 'm12345'
        self.url = '{}://legacy.{}/content/{}/latest'.format(
            self.request.scheme,
            self.request.domain,
            self.id,
        )

    def test_success(self, requests_mock):
        request_callback = pretend.call_recorder(
            lambda request, context: 'updated')
        # Mock the request
        requests_mock.register_uri('GET', rmock.ANY, text=request_callback)

        # Call the target
        self.target(self.celery_task, self.url)

        # Check for request calls
        request, context = request_callback.calls[0].args
        assert request.url == self.url

        # Check for logging
        assert len(self.request.log.info.calls) == 0
        assert len(self.request.log.debug.calls) == 0
        assert len(self.request.log.exception.calls) == 0

    def test_custom_request_method(self, requests_mock):
        request_callback = pretend.call_recorder(
            lambda request, context: 'ok')
        # Mock the request
        request_method = 'KISS'
        requests_mock.register_uri(
            request_method,
            rmock.ANY,
            text=request_callback,
        )

        # Call the target
        self.target(self.celery_task, self.url, method=request_method)

        # Check for request calls
        request, context = request_callback.calls[0].args
        assert request.url == self.url
        assert request.method == request_method

        # Check for logging
        assert len(self.request.log.info.calls) == 0
        assert len(self.request.log.debug.calls) == 0
        assert len(self.request.log.exception.calls) == 0

    def test_failed_request_and_retry(self, requests_mock):

        @count_calls
        def request_callback(request, context):
            if request_callback.call_count < 2:
                raise requests.exceptions.ConnectTimeout()
            else:
                return 'updated'

        # mock a problem request to enqueue
        requests_mock.register_uri('GET', self.url, text=request_callback)

        # Call the target
        self.target(self.celery_task, self.url)

        # Check that the retry method was called
        assert len(self.task_retry_method.calls) == 1

        # Make sure the requests_mock callback was called several times
        assert request_callback.call_count == 2

        # Check raven was used...
        assert self.request.raven_client.captureException.calls == []

        # Check for logging
        assert self.request.log.info.calls == []
        assert self.request.log.debug.calls == []
        assert self.request.log.exception.calls == [
            pretend.call("problem requesting '{}'".format(self.url)),
        ]

    def test_max_retries(self, requests_mock):
        # Note:
        #     Because we directly call the target function as part of
        #     celery task retry, the error cascades through the stack.
        #     This is not the usual Celery behavior,
        #     for the sake of testing it works just fine.
        #     To work around this we'd have to start a valid worker
        #     subprocess. That's more complicated and error prone.

        @count_calls
        def request_callback(request, context):
            raise requests.exceptions.ConnectTimeout()

        # mock a problem request to enqueue
        requests_mock.register_uri('GET', self.url, text=request_callback)

        # Call the target
        with pytest.raises(FauxMaxRetriesExceededError):
            self.target(self.celery_task, self.url)

        # Check that the retry method was called
        assert len(self.task_retry_method.calls) == self.max_retries

        # Make sure the requests_mock callback was called several times
        assert request_callback.call_count == self.max_retries

        # Check raven was used...
        expected = [
            pretend.call(),
            # See note at the top of this test function.
            # The following are cascading calls due to the execption rolling
            # through the stack.
            pretend.call(),
            pretend.call(),
            pretend.call(),
        ]
        assert self.request.raven_client.captureException.calls == expected

        # Check for logging
        assert self.request.log.info.calls == []
        assert self.request.log.debug.calls == []
        # See note at the top of this test function.
        # There should be exception log calls, but because of the nature
        # of our retry() method, we aren't able to continue through the logic.
        assert self.request.log.exception.calls == []
