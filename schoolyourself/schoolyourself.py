"""The base class for School Yourself XBlocks."""

import os
import pkg_resources

from mako.template import Template

from xblock.core import XBlock
from xblock.fragment import Fragment


class SchoolYourselfXBlock(XBlock):
    """
    This block renders a launcher button for a School Yourself lesson,
    which is rendered in an iframe. The block transmits the anonymous
    user ID and has a handler that receives information from School
    Yourself regarding the user's progress and mastery through the
    topic being shown.
    """
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


    def get_partner_url_params(self):
      url_params = {"id": self.module_id,
                    "partner": "edx"}
      user_id = self.get_student_id()
      if user_id:
        url_params["partner_user_id"] = user_id

      return url_params


    def studio_view(self, context=None):
      """
      This is the view that content authors will see when they click on the
      "Edit" button in Studio. It is a form that lets them type in two fields:
      module ID and player type. This is the same for both lessons and
      reviews.
      """
      context = {
        "module_id": self.module_id,
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
      if "shared_key" in data:
        self.shared_key = data.get("shared_key")

      return { "module_id": self.module_id,
               "shared_key": self.shared_key }
