"""An XBlock that displays School Yourself reviews and may publish grades."""

import urllib

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment

from schoolyourself import SchoolYourselfXBlock


class SchoolYourselfReviewXBlock(SchoolYourselfXBlock):
    """
    This block renders a launcher button for a School Yourself review,
    which is rendered in an iframe. The block transmits the anonymous
    user ID and has a handler that receives information from School
    Yourself regarding the user's progress and mastery through the
    topic being shown.
    """
    has_children = False
    has_score = True
    weight = 1.0

    def student_view(self, context=None):
      """
      The primary view of the SchoolYourselfReviewXBlock, shown to students
      when viewing courses.
      """
      # Construct the URL we're going to stuff into the iframe once
      # it gets launched:
      url_params = self.get_partner_url_params(self.shared_key)
      url_params["module"] = self.module_id

      # Set up the screenshot URL:
      screenshot_url = "%s/page/screenshot/%s" % (self.base_url,
                                                  self.module_id)

      context = {
        "iframe_url": "%s/review/embed?%s" % (self.base_url,
                                              urllib.urlencode(url_params)),
        "module_title": self.module_title,
        "icon_url": self.runtime.local_resource_url(self,
                                                    "public/review_icon.png")
      }

      # Now actually render the fragment, which is just a button with
      # some JS code that handles the click event on that button.
      fragment = Fragment(self.render_template("review_student_view.html",
                                               context))

      # Load the common JS/CSS libraries:
      fragment.add_css_url(
        self.runtime.local_resource_url(self, "public/sylib.css"))
      fragment.add_javascript_url(
        self.runtime.local_resource_url(self, "public/sylib.js"))


      # And finally the embedded HTML/JS code:
      fragment.add_javascript(self.resource_string(
          "static/js/review_student_view.js"))
      fragment.add_css(self.resource_string(
          "static/css/student_view.css"))
      fragment.initialize_js("SchoolYourselfReviewStudentView")
      return fragment


    @XBlock.json_handler
    def handle_grade(self, data, suffix=""):
      """This is the handler that gets called when we receive grades.

      TODO(jjl): Make sure the message is signed.
      """
      mastery = data.get("m", None)
      if not mastery:
        return

      self.runtime.publish(self, "grade",
                           { "value": mastery,
                             "max_value": 0.7 })


    @staticmethod
    def workbench_scenarios():
      """A canned scenario for display in the workbench."""
      return [
        ("SchoolYourselfReviewXBlock",
         """\
            <vertical_demo>
              <schoolyourself_review
                  base_url="http://localhost:9753"
                  module_id="algebra/multiplication"
                  shared_key="test"
              />
            </vertical_demo>
         """),
        ]
