# Copyright (C) 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for events.py."""

__author__ = 'ricbit@google.com (Ricardo Bittencourt)'

import unittest

import events

class Generic():
  pass

class EventsTest(unittest.TestCase):

  def _CreateProblems(self, solved, unsolved):
    metadata = Generic()
    metadata.problems = []
    def AddProblem(problems, is_solved):
      for code in problems:
	problem = Generic()
	problem.code = code
	problem.solved = is_solved
	metadata.problems.append(problem)
    AddProblem(solved, True)	
    AddProblem(unsolved, False)	
    return metadata

  def testGenerateEvents(self):
    old = self._CreateProblems(
        solved=['TEST', 'MUL'],
	unsolved=['PRIM', 'CPRIM'])
    new = self._CreateProblems(
        solved=['TEST', 'CPRIM', 'SHPATH'], 
	unsolved=['MUL'])
    event_list = events.GenerateEvents(old, new)
    self.assertTrue(all(isinstance(event, events.ProblemEvent))
                    for event in event_list)
    self.assertEquals(2, len(event_list))
    check = lambda code: any(event.code == code for event in event_list)
    self.assertTrue(all(check(code) for code in ['CPRIM', 'SHPATH']))

  def testGenerateEventsWithOldNone(self):
    new = self._CreateProblems(
        solved=['TEST', 'CPRIM', 'SHPATH'], 
	unsolved=['MUL'])
    event_list = events.GenerateEvents(None, new)
    self.assertTrue(all(isinstance(event, events.ProblemEvent))
                    for event in event_list)
    self.assertEquals(3, len(event_list))
    check = lambda code: any(event.code == code for event in event_list)
    self.assertTrue(all(check(code) for code in ['CPRIM', 'SHPATH', 'TEST']))

if __name__ == '__main__':
  unittest.main()
