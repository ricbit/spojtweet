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

"""Events interface."""

__author__ =  'ricbit@google.com (Ricardo Bittencourt)'

import datetime

class Event(object):
  pass

class NewProblemEvent(Event):
  def __init__(self, code):
    self.code = code

def GenerateEvents(old_metadata, new_metadata):
  event_list = []
  solved = lambda problems: set(prob.code for prob in problems if prob.solved)
  old_solved_problems = solved(old_metadata.problems)
  new_solved_problems = solved(new_metadata.problems)
  for code in new_solved_problems - old_solved_problems:
    event_list.append(NewProblemEvent(code))
  return event_list
