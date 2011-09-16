import unittest

import badge

class BadgeTest(unittest.TestCase):

  def testGrantBadgesForEmptyMetadata(self):
    metadata = badge.UserMetadata()
    badges = badge.GrantBadges(metadata)
    self.assertTrue(len(badges) == 0)


if __name__ == '__main__':
  unittest.main()
