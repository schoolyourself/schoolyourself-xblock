"""An XBlock that displays School Yourself lessons and may publish grades."""

import urllib

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment

from schoolyourself import SchoolYourselfXBlock


class SchoolYourselfLessonXBlock(SchoolYourselfXBlock):
    """
    This block renders a launcher button for a School Yourself lesson,
    which is rendered in an iframe. The block transmits the anonymous
    user ID and has a handler that receives information from School
    Yourself regarding the user's progress and mastery through the
    topic being shown.
    """
    has_children = False
    has_score = False

    module_id = String(
      help=("The full ID of the module as it would appear on "
            "schoolyourself.org, such as 'geometry/lines_rays'."),
      scope=Scope.settings,
      default="intro/intro_module",
      display_name="SY Module ID",
      enforce_type=True)

    base_url = String(
      help=("The base URL that the iframes will be pointing to. Do not put "
            "URL params here -- those get added by the view."),
      default="https://dev.schoolyourself.org/page",
      scope=Scope.content,
      display_name="Base URL",
      enforce_type=True)

    shared_key = String(
      help=("This is the key that we use to verify signed data coming "
            "from the School Yourself server about the user. This typically "
            "includes the user ID and mastery levels of the topic presented "
            "in this lesson."),
      scope=Scope.content,
      display_name="Shared key",
      default="",
      enforce_type=True)


    def student_view(self, context=None):
      """
      The primary view of the SchoolYourselfLessonXBlock, shown to students
      when viewing courses.
      """
      # Construct the URL we're going to stuff into the iframe once
      # it gets launched:
      url_params = self.get_partner_url_params()

      # Set up the screenshot URL:
      screenshot_url = "%s/screenshot/%s" % (self.base_url, self.module_id)

      context = {
        "iframe_url": "%s/player?%s" % (self.base_url,
                                       urllib.urlencode(url_params)),
        "screenshot_url": screenshot_url
      }

      # Now actually render the fragment, which is just a button with
      # some JS code that handles the click event on that button.
      fragment = Fragment(self.render_template("student_view.html", context))

      # Load the common JS/CSS libraries:
      fragment.add_css_url(
        self.runtime.local_resource_url(self, "public/sylib.css"))
      fragment.add_javascript_url(
        self.runtime.local_resource_url(self, "public/sylib.js"))

      # An example of grading:
      # self.runtime.publish(self, "grade",
      #                     { "value": 70,
      #                       "max_value": 100 })

      # And finally the embedded HTML/JS code:
      fragment.add_javascript(self.resource_string(
          "static/js/student_view.js"))
      fragment.add_css(self.resource_string(
          "static/css/student_view.css"))
      fragment.initialize_js("SchoolYourselfStudentView")
      return fragment


    @staticmethod
    def workbench_scenarios():
      """A canned scenario for display in the workbench."""
      return [
        ("SchoolYourselfLessonXBlock",
         """\
            <vertical_demo>
              <schoolyourself_lesson
                  module_id="geometry/lines_rays"
              />
            </vertical_demo>
         """),
        ]
