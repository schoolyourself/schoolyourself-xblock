"""This file contains a unit test for the SchoolYourselfReviewXBlock."""

import unittest

from .schoolyourself_review import SchoolYourselfReviewXBlock

from unittest.mock import Mock
from xblock.fields import ScopeIds
from xblock.field_data import DictFieldData


class FakeXModuleRuntime:
  """
  Depending on whether we're running in the LMS or in the XBlock
  workbench, the "xmodule_runtime" attr may or may not be set (in
  the LMS, it's set, and that's what production uses). The only field
  we ever look at in our XBlock code is "anonymous_student_id",
  so this is a dummy object that holds that.
  """
  def __init__(self, anonymous_student_id):
    self.anonymous_student_id = anonymous_student_id


class SchoolYourselfReviewXBlockTest(unittest.TestCase):
  def setUp(self):
    self.mock_runtime = Mock()
    self.block = SchoolYourselfReviewXBlock(self.mock_runtime,
                                            DictFieldData({}),
                                            ScopeIds("foo", "bar", "baz", "x"))

    # This is a fake shared key and a manually computed signature for use
    # in this test.
    self.block.shared_key = "key"
    self.canned_signature = "f0cc345470c322e0c6f41d541fe2b736"


  def test_default_params(self):
    self.assertFalse(SchoolYourselfReviewXBlock.has_children)
    self.assertTrue(SchoolYourselfReviewXBlock.has_score)
    self.assertAlmostEqual(SchoolYourselfReviewXBlock.weight, 1.0)


  def test_display_name(self):
    """
    Make sure we are correctly overriding the get_display_name() of
    the base class.
    """
    self.assertEqual(self.block.get_display_name("blah"), "Review: blah")


  def test_student_id(self):
    self.assertEqual(self.block.get_student_id(), "debug")
    self.block.xmodule_runtime = FakeXModuleRuntime("abc123")
    self.assertEqual(self.block.get_student_id(), "abc123")


  def test_handle_grade_malformed_input(self):
    self.block.module_id = "algebra/multiplication"

    self.assertEqual(self.block.handle_grade_json("foo"), "bad_request")
    self.assertEqual(self.block.handle_grade_json(["foo"]), "bad_request")
    self.assertEqual(self.block.handle_grade_json({}), "forbidden")
    self.assertEqual(self.block.handle_grade_json(
        {"mastery": {"invalid_module_id": 1.0},
         "user_id": "foo",
         "signature": "asdf"}), "bad_request")

    # Make sure we never publish any grades for situations like this.
    self.assertEqual(len(self.mock_runtime.publish.method_calls), 0)


  def test_handle_grade_malformed_signed_input(self):
    """
    This is a test for an unlikely situation where the input is malformed
    but the signature is somehow correct. We should at least not start
    throwing errors.
    """
    self.block.module_id = "algebra/multiplication"

    self.assertEqual(self.block.handle_grade_json(
        {"mastery": {"algebra/multiplication": "hello"},  # A non-number!
         "user_id": "foo",
         "signature": self.canned_signature}), "bad_request")


  def test_handle_grade(self):
    self.block.module_id = "algebra/multiplication"

    self.assertEqual(self.block.handle_grade_json(
        {"mastery": {"algebra/multiplication": 0.7},
         "user_id": "foo",
         "signature": "asdf"}), "invalid_signature")

    # Invalid signatures should never publish grades.
    self.assertEqual(len(self.mock_runtime.publish.method_calls), 0)

    self.assertEqual(self.block.handle_grade_json(
        {"mastery": {"algebra/multiplication": 0.7},
         "user_id": "foo",
         "signature": self.canned_signature}), 1.0)

    self.mock_runtime.publish.assert_called_with(self.block, "grade",
                                                 { "value": 1.0,
                                                   "max_value": 1.0 })


  def test_get_partner_url_params(self):
    # These are the defaults:
    self.assertEqual(self.block.get_partner_url_params(),
                     { "partner": "edx",
                       "partner_user_id": "debug" })

    self.block.partner_id = "foo"
    self.block.xmodule_runtime = FakeXModuleRuntime("abc123")

    self.assertEqual(self.block.get_partner_url_params(),
                     { "partner": "foo",
                       "partner_user_id": "abc123" })


if __name__ == "__main__":
  unittest.main()
