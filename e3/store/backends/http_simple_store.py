from __future__ import absolute_import


import e3.hash
import e3.log
from e3.net.http import HTTPSession
from e3.store.backends.base import ResourceInfo, Store


logger = e3.log.getLogger('store.httpsimplestore')


class HTTPSimpleStoreResourceInfo(ResourceInfo):

    def __init__(self, url, sha):
        self.url = url
        self.sha = sha

    def verify(self, resource_path):
        resource_sha = e3.hash.sha1(resource_path)
        if resource_sha != self.sha:
            logger.critical('wrong sha for resource %s '
                            'expecting %s got %s',
                            resource_path, self.sha,
                            resource_sha)
        else:
            return True

    @property
    def uid(self):
        return self.sha


class HTTPSimpleStore(Store):

    def get_resource_metadata(self, query):
        """Return resource metadata directly computed from the query.

        There is no remote server involved here.
        :param query: a dict containing two keys 'sha' and 'url'. sha is the
            sha1sum of the resource and url is the remote url
        :type query:
        """
        assert 'sha' in query and 'url' in query
        return HTTPSimpleStoreResourceInfo(query['url'], query['sha'])

    def download_resource_content(self, metadata, dest):
        """Download a resource.

        :param metadata: metadata associated with the resource to download
        :type metadata: HTTPSimpleStoreResourceInfo
        :param dest:
        :type dest: str
        :return: the path to the downloaded resource
        :rtype: str
        """
        with HTTPSession() as http:
            path = http.download_file(metadata.url, dest)
            if path is None:
                return None
            elif not metadata.verify(path):
                # Error when downloading the resource?
                return None
            else:
                return path