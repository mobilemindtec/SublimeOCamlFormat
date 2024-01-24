import os
import sublime
import sublime_plugin
import subprocess
import tempfile

# The "c" in "Ocaml" is intentionally uncapitalized in this class name, in order to
# ensure that its snake-case form is "ocaml_format", rather than the less-intuitive
# "o_caml_format". Sublime Text's command system relies on snake-case inflections of
# class names.
class OcamlFormatCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        region = sublime.Region(0, self.view.size())
        text = self.view.substr(region)

        tmpfd, tmppath = tempfile.mkstemp()
        try:
            os.write(tmpfd, bytes(text, "UTF-8"))
            os.close(tmpfd)


            ret = subprocess.call("ocamlformat --inplace --profile=default --enable-outside-detected-project %s" % (tmppath), shell=True)
            if ret != 0:
                print("ocamlformat error: ", ret)
                return


            with open(tmppath, "r", -1, "UTF-8") as f:
                r = f.read()
                self.view.replace(edit, region, r)
        finally:
            try:
                os.close(tmpfd)
            except OSError:
                # Ignore errors if tmpfd is already closed
                pass
            finally:
                os.unlink(tmppath)


class OCamlFormatListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        _, ext = os.path.splitext(view.file_name())
        if ext != ".ml":
            return

        view.run_command("ocaml_format")

