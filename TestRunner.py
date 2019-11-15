from unittest import TestLoader, TestSuite
from Tests.test_Osu_One import OsuAutomationOne
from Tests.test_Osu_Two import OsuAutomationTwo
from Tests.test_Osu_Three import OsuAutomationThree

import testtools

if __name__ == "__main__":

    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(OsuAutomationOne),
        loader.loadTestsFromTestCase(OsuAutomationTwo),
        loader.loadTestsFromTestCase(OsuAutomationThree)
        ))

    concurrent_suite = testtools.ConcurrentStreamTestSuite(lambda: ((case, None) for case in suite))
    concurrent_suite.run(testtools.StreamResult())
