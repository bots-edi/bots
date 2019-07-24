# -*- coding: utf-8 -*-

import unittest
from bots.botslib import Uri

"""no plugin
"""


class TestTranslate(unittest.TestCase):
    def setUp(self):
        pass

    def testcombinations(self):
        self.assertEqual(
            "scheme://username:password@hostname:80/path1/path2/filename",
            str(
                Uri(
                    scheme="scheme",
                    username="username",
                    password="password",
                    hostname="hostname",
                    port=80,
                    path="path1/path2",
                    filename="filename",
                    query={"query": "argument"},
                    fragment="fragment",
                )
            ),
            "basis",
        )
        self.assertEqual(
            "scheme://username:password@hostname:80/path1/path2/filename",
            str(
                Uri(
                    scheme="scheme",
                    username="username",
                    password="password",
                    hostname="hostname",
                    port=80,
                    path="path1/path2",
                    filename="filename",
                )
            ),
            "basis",
        )

        self.assertEqual(
            "scheme:/path1/path2/filename",
            str(Uri(scheme="scheme", path="/path1/path2", filename="filename")),
            "",
        )
        self.assertEqual(
            "scheme:path1/path2/filename",
            str(Uri(scheme="scheme", path="path1/path2", filename="filename")),
            "",
        )
        self.assertEqual(
            "path1/path2/filename",
            str(Uri(path="path1/path2", filename="filename")),
            "",
        )
        self.assertEqual("path1/path2/", str(Uri(path="path1/path2")), "")
        self.assertEqual("filename", str(Uri(filename="filename")), "")
        self.assertEqual(
            "scheme:path1/path2/", str(Uri(scheme="scheme", path="path1/path2")), ""
        )
        self.assertEqual(
            "scheme:filename", str(Uri(scheme="scheme", filename="filename")), ""
        )

        self.assertEqual(
            "scheme://username:password@hostname:80/path1/path2/",
            str(
                Uri(
                    scheme="scheme",
                    username="username",
                    password="password",
                    hostname="hostname",
                    port=80,
                    path="path1/path2",
                )
            ),
            "basis",
        )
        self.assertEqual(
            "scheme://username:password@hostname:80/filename",
            str(
                Uri(
                    scheme="scheme",
                    username="username",
                    password="password",
                    hostname="hostname",
                    port=80,
                    filename="filename",
                )
            ),
            "basis",
        )
        self.assertEqual(
            "scheme://username:password@hostname:80",
            str(
                Uri(
                    scheme="scheme",
                    username="username",
                    password="password",
                    hostname="hostname",
                    port=80,
                )
            ),
            "bas",
        )
        self.assertEqual(
            "scheme://username:password@hostname",
            str(
                Uri(
                    scheme="scheme",
                    username="username",
                    password="password",
                    hostname="hostname",
                )
            ),
            "bas",
        )
        self.assertEqual(
            "scheme://username@hostname",
            str(Uri(scheme="scheme", username="username", hostname="hostname")),
            "bas",
        )
        self.assertEqual(
            "scheme://hostname", str(Uri(scheme="scheme", hostname="hostname")), "bas"
        )

        self.assertEqual(
            "scheme://username@hostname:80/path1/path2/filename",
            str(
                Uri(
                    scheme="scheme",
                    username="username",
                    hostname="hostname",
                    port=80,
                    path="path1/path2",
                    filename="filename",
                )
            ),
            "no password",
        )
        self.assertEqual(
            "scheme://hostname:80/path1/path2/filename",
            str(
                Uri(
                    scheme="scheme",
                    password="password",
                    hostname="hostname",
                    port=80,
                    path="path1/path2",
                    filename="filename",
                )
            ),
            "no username",
        )
        self.assertEqual(
            "scheme:path1/path2/filename",
            str(
                Uri(
                    scheme="scheme",
                    username="username",
                    password="password",
                    path="path1/path2",
                    filename="filename",
                )
            ),
            "no hostname",
        )
        self.assertEqual(
            "//username:password@hostname:80/path1/path2/filename",
            str(
                Uri(
                    username="username",
                    password="password",
                    hostname="hostname",
                    port=80,
                    path="path1/path2",
                    filename="filename",
                )
            ),
            "no scheme",
        )
        self.assertEqual(
            "path1/path2/filename",
            str(
                Uri(
                    username="username",
                    password="password",
                    port=80,
                    path="path1/path2",
                    filename="filename",
                )
            ),
            "no scheme no hostname",
        )

    def testempty(self):
        # tests for empty values
        self.assertEqual(
            "//username:password@hostname:80/path1/path2/filename",
            str(
                Uri(
                    scheme=None,
                    username="username",
                    password="password",
                    hostname="hostname",
                    port=80,
                    path="path1/path2",
                    filename="filename",
                )
            ),
            "basis",
        )
        self.assertEqual(
            "//username:password@hostname:80/path1/path2/filename",
            str(
                Uri(
                    scheme="",
                    username="username",
                    password="password",
                    hostname="hostname",
                    port=80,
                    path="path1/path2",
                    filename="filename",
                )
            ),
            "basis",
        )
        self.assertEqual(
            "scheme://hostname:80/path1/path2/filename",
            str(
                Uri(
                    scheme="scheme",
                    username=None,
                    password=None,
                    hostname="hostname",
                    port=80,
                    path="path1/path2",
                    filename="filename",
                )
            ),
            "basis",
        )
        self.assertEqual(
            "scheme://hostname:80/path1/path2/filename",
            str(
                Uri(
                    scheme="scheme",
                    username="",
                    password="",
                    hostname="hostname",
                    port=80,
                    path="path1/path2",
                    filename="filename",
                )
            ),
            "basis",
        )
        # ~ self.assertEqual('scheme://username:password@hostname:80/path1/path2/filename',str(Uri(scheme='scheme',username='username',password='password',hostname='hostname',port=80,path='path1/path2',filename= 'filename')),'basis')

    def testcalls(self):
        self.assertEqual(
            "scheme:/path1/path2/filename2",
            Uri(scheme="scheme", path="/path1/path2", filename="filename").uri(
                filename="filename2"
            ),
            "",
        )


if __name__ == "__main__":
    unittest.main()
