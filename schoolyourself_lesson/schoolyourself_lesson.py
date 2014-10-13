"""An XBlock that displays School Yourself lessons and may publish grades."""

import os
import pkg_resources
import urllib

from mako.template import Template
from mako.lookup import TemplateLookup

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, Boolean, Float
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

    module_id = String(
      help=("The full ID of the module as it would appear on "
            "schoolyourself.org, such as 'geometry/lines_rays'."),
      scope=Scope.settings,
      default="intro/intro_module",
      display_name="SY Module ID",
      enforce_type=True)

    player_type = String(
      help=("A string, one of 'module' or 'review', which indicates whether "
            "this is a regular lesson or an assessment. This only affects "
            "the iframe URL that we end up pointing to."),
      scope=Scope.settings,
      display_name="Type",
      default="module",
      enforce_type=True,
      values=[{"display_name": "Module", "value": "module"},
              {"display_name": "Review", "value": "review"}])

    has_score = Boolean(
      help="Whether this block participates in the course grade.",
      scope=Scope.settings,
      default=True,
      display_name="Has score")

    weight = Float(
      help="The contribution of this block to the score.",
      scope=Scope.settings,
      default=1.0,
      display_name="Weight")

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
            "in this lesson."),
      scope=Scope.content,
      display_name="Shared key",
      default="",
      enforce_type=True)


    def resource_string(self, path):
      """Handy helper for getting resources from our kit."""
      data = pkg_resources.resource_string(__name__, path)
      return data.decode("utf8")


    def render_template(self, template_name, context={}):
      """Another handy helper for rendering Mako templates from our kit."""

      template = Template(self.resource_string(os.path.join("templates",
                                                            template_name)))
      return template.render_unicode(**context)


    def student_view(self, context=None):
      """
      The primary view of the SchoolYourselfLessonXBlock, shown to students
      when viewing courses.
      """
      # Construct the URL we're going to stuff into the iframe once
      # it gets launched:
      url_params = urllib.urlencode({"id": self.module_id})
      context = {
        "iframe_url": "%s?%s" % (self.embed_url, url_params)
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
      fragment.initialize_js("SchoolYourselfStudentView")
      return fragment


    def studio_view(self, context=None):
      """
      This is the view that content authors will see when they click on the
      "Edit" button in Studio. It is a form that lets them type in two fields:
      module ID and player type.
      """
      context = {
        "module_id": self.module_id,
        "player_type": self.player_type,
        "shared_key": self.shared_key,
      }

      fragment = Fragment(self.render_template("studio_view.html", context))

      fragment.add_javascript(
        self.resource_string("static/js/studio_view.js"))
      fragment.initialize_js("SchoolYourselfStudioView")
      return fragment


    @XBlock.json_handler
    def studio_submit(self, data, suffix=""):
      """
      This is the handler that the form in student_view() calls when
      new data is inputted.
      """
      self.module_id = data.get("module_id", "intro/intro_module")
      player_type = data.get("player_type", "module")
      if player_type != "module" and player_type != "review":
        player_type = "module"
      self.player_type = player_type

      if "shared_key" in data:
        self.shared_key = data.get("shared_key")

      return { "module_id": self.module_id,
               "player_type": self.player_type,
               "shared_key": self.shared_key }


    @staticmethod
    def workbench_scenarios():
      """A canned scenario for display in the workbench."""
      return [
        ("SchoolYourselfLessonXBlock",
         """\
            <vertical_demo>
              <schoolyourself_lesson
                  module_id="geometry/lines_rays"
                  player_type="module"
              />
            </vertical_demo>
         """),
        ]
