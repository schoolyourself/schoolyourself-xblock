"""An XBlock that displays School Yourself lessons and may publish grades."""

import pkg_resources
import urllib

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment


class SchoolYourselfLessonXBlock(XBlock):
    """
    This block renders a launcher button for a School Yourself lesson,
    which is rendered in an iframe. The block transmits the anonymous
    user ID and has a handler that receives information from School
    Yourself regarding the user's progress and mastery through the
    topic being shown.
    """
    has_children = False
    has_score = True

    module_id = String(
      help=("The full ID of the module as it would appear on "
            "schoolyourself.org, such as 'geometry/lines_rays'."),
      scope=Scope.settings,
      display_name="SY Module ID",
      enforce_type=True)

    player_type = String(
      help=("A string, one of 'module' or 'review', which indicates whether "
            "this is a regular lesson or an assessment. This only affects "
            "the iframe URL that we end up pointing to."),
      scope=Scope.settings,
      display_name="Type",
      enforce_type=True,
      values=[{"display_name": "Module", "value": "module"},
               {"display_name": "Review", "value": "review"}])

    embed_url = String(
      help=("The base URL that the iframes will be pointing to. Do not put "
            "URL params here -- those get added by the view."),
      default="https://dev.schoolyourself.org/page/player",
      scope=Scope.content,
      display_name="Base URL",
      enforce_type=True)

    shared_key = String(
      help=("This is the key that we use to verify signed data coming "
            "from the School Yourself server about the user. This typically "
            "includes the user ID and mastery levels of the topic presented "
            "in this XBlock."),
      scope=Scope.content,
      display_name="Shared key",
      enforce_type=True)


    def resource_string(self, path):
      """Handy helper for getting resources from our kit."""
      data = pkg_resources.resource_string(__name__, path)
      return data.decode("utf8")


    def student_view(self, context=None):
      """
      The primary view of the SchoolYourselfLessonXBlock, shown to students
      when viewing courses.
      """
      # Construct the URL we're going to hit:
      url_params = urllib.urlencode({"id": self.module_id})
      iframe_url = "%s?%s" % (self.embed_url, url_params)

      html = self.resource_string("static/html/schoolyourself_lesson.html")
      fragment = Fragment(html.format(self=self, url=iframe_url))

      #fragment.add_css(self.resource_string("static/css/schoolyourself-lesson.css"))
      #fragment.add_javascript(self.resource_string("static/js/src/schoolyourself-lesson.js"))
      #fragment.initialize_js('SchoolYourselfLessonXBlock')
      return fragment


    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("SchoolYourselfLessonXBlock",
             """<vertical_demo>
                <schoolyourself_lesson module_id="geometry/lines_rays" player_type="module"/>
                </vertical_demo>
             """),
        ]
