"""The base class for School Yourself XBlocks (lessons and reviews)."""

import hmac
import os
import pkg_resources

from mako.template import Template

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment


class SchoolYourselfXBlock(XBlock):
    """Common functionality for the School Yourself XBlocks.

    The School Yourself XBlocks (SchoolYourselfLessonXBlock and
    SchoolYourselfReviewXBlock) are very similar in that both of them
    show iframes that point to another location.

    The "Lesson" XBlock points the introduction page for one of our
    lessons and allows them to continue navigating whatever branches
    they choose to follow until they reach the "end" page for that
    lesson. These do not contribute to the grade, and the user may
    actually choose to skip it if they want to.

    The "Review" XBlock points to an adaptive assessment for a given
    lesson. This DOES participate in the course grade, and requires that
    users reach a certain mastery level before it shows a message
    telling them that they can quit. The user may quit at any point
    and resume later. Note that a user's grade may *decrease* if they
    master the topic, then come back later and get subsequent
    questions wrong.
    """
    display_name = String(
      help="The display name of this component.",
      scope=Scope.settings,
      default="",
      display_name="The display name of this component")

    module_id = String(
      help=("The full ID of the module as it would appear on "
            "schoolyourself.org, such as 'geometry/lines_rays'."),
      scope=Scope.settings,
      default="intro/intro_module",
      display_name="SY Module ID",
      enforce_type=True)

    module_title = String(
      help=("The human-readable title of the module, such as "
            "'Lines and rays'."),
      scope=Scope.settings,
      default="Introduction",
      display_name="SY Module name",
      enforce_type=True)

    module_description = String(
      help=("The description text to display underneath the title."),
      scope=Scope.settings,
      default="Welcome to School Yourself!",
      display_name="SY Module description",
      enforce_type=True)

    base_url = String(
      help=("The base URL that the iframes will be pointing to. Do not put "
            "URL params here -- those get added by the view."),
      default="https://schoolyourself.org",
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


    def get_student_id(self):
      """This is a helper that retrieves the student ID. We need this
      method because the ID might be different depending on whether we
      are running in the LMS or in the XBlock workbench. For more
      information, see
      https://groups.google.com/forum/#!topic/edx-code/ryPw7a-tK_g
      for a discussion on this topic.

      If no student ID is available for some reason, we return None.

      Returns:
          A unicode string.
      """
      if hasattr(self, "xmodule_runtime"):
        return self.xmodule_runtime.anonymous_student_id

      # The following lines give an alternate way of getting a user_id
      # in the case of studio or workbench. Currently, studio will
      # just give back an ID of "student", whereas workbench lets you
      # set it in a URL param. In any case, any module that is not being
      # actually viewed by a student should send the user ID "debug"
      # back to the SY servers. If you want to change that behavior,
      # uncomment the following 3 lines.
      #
      # if self.scope_ids.user_id is None:
      #   return None
      # return unicode(self.scope_ids.user_id)

      return "debug"


    def resource_string(self, path):
      """Handy helper for getting resources from our kit."""
      data = pkg_resources.resource_string(__name__, path)
      return data.decode("utf8")


    def render_template(self, template_name, context={}):
      """Another handy helper for rendering Mako templates from our kit."""

      template = Template(self.resource_string(os.path.join("templates",
                                                            template_name)))
      return template.render_unicode(**context)


    def get_partner_url_params(self, shared_key=None):
      """A helper method that generates a dict of URL params that we can
      append to the end of a URL, containing the partner ID and the
      user's anonymouse user ID. These are typically transmitted as URL
      params. in the iframes.

      If a shared_key is provided and there is a username to encode,
      we will sign it with the shared key.
      """
      url_params = {"partner": "edx"}
      user_id = self.get_student_id()
      if user_id:
        url_params["partner_user_id"] = user_id
        if shared_key:
          url_params["partner_signature"] = hmac.new(str(shared_key),
                                                     user_id).hexdigest()

      return url_params


    def get_display_name(self, module_title):
      """
      This method generates a string that is usable as the display name
      for the component, using the module title (such as "Lines and Rays").
      By default, we just return the module title, but subclasses might
      want to do something more specific.
      """
      return module_title


    def studio_view(self, context=None):
      """
      This is the view that content authors will see when they click on the
      "Edit" button in Studio. It is a form that lets them type in two fields:
      module ID and player type. This is the same for both lessons and
      reviews.
      """
      context = {
        "module_id": self.module_id,
        "module_title": self.module_title,
        "module_description": self.module_description,
        "shared_key": self.shared_key,
        "base_url": self.base_url
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
      self.module_title = data.get("module_title", "Introduction")
      self.module_description = data.get("module_description",
                                         "Welcome to School Yourself!")
      self.base_url = data.get("base_url",
                               "https://schoolyourself.org")
      if "shared_key" in data:
        self.shared_key = data.get("shared_key")

      self.display_name = self.get_display_name(self.module_title)

      return { "module_id": self.module_id,
               "module_title": self.module_title,
               "module_description": self.module_description,
               "shared_key": self.shared_key,
               "base_url": self.base_url }
