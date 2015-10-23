"""
EvEditor (Evennia Line Editor)

This implements an advanced line editor for editing longer texts
in-game. The editor mimics the command mechanisms of the "VI" editor
(a famous line-by-line editor) as far as reasonable.

Features of the editor:

 - undo/redo.
 - edit/replace on any line of the buffer.
 - search&replace text anywhere in buffer.
 - formatting of buffer, or selection, to certain width + indentations.
 - allow to echo the input or not, depending on your client.

To use the editor, just import EvEditor from this module
and initialize it:

    from evennia.utils.eveditor import EvEditor

    EvEditor(caller, loadfunc=None, savefunc=None, quitfunc=None, key="")

 - caller is the user of the editor, the one to see all feedback.
 - loadfunc(caller) is called when the editor is first launched; the
   return from this function is loaded as the starting buffer in the
   editor.
 - safefunc(caller, buffer) is called with the current buffer when
   saving in the editor. The function should return True/False depending
   on if the saving was successful or not.
 - quitfunc(caller) is called when the editor exits. If this is given,
   no automatic quit messages will be given.
 - key is an optional identifier for the editing session, to be
   displayed in the editor.

"""

import re
from django.conf import settings
from evennia import Command, CmdSet
from evennia.utils import is_iter, fill, dedent
from evennia.commands import cmdhandler

# we use cmdhandler instead of evennia.syscmdkeys to
# avoid some cases of loading before evennia init'd
_CMD_NOMATCH = cmdhandler.CMD_NOMATCH
_CMD_NOINPUT = cmdhandler.CMD_NOINPUT

_RE_GROUP = re.compile(r"\".*?\"|\'.*?\'|\S*")
# use NAWS in the future?
_DEFAULT_WIDTH = settings.CLIENT_DEFAULT_WIDTH

#------------------------------------------------------------
#
# texts
#
#------------------------------------------------------------

_HELP_TEXT = \
"""
 <txt>  - any non-command is appended to the end of the buffer.
 :  <l> - view buffer or only line <l>
 :: <l> - view buffer without line numbers or other parsing
 :::    - print a ':' as the only character on the line...
 :h     - this help.

 :w     - save the buffer (don't quit)
 :wq    - save buffer and quit
 :q     - quit (will be asked to save if buffer was changed)
 :q!    - quit without saving, no questions asked

 :u     - (undo) step backwards in undo history
 :uu    - (redo) step forward in undo history
 :UU    - reset all changes back to initial state

 :dd <l>     - delete line <n>
 :dw <l> <w> - delete word or regex <w> in entire buffer or on line <l>
 :DD         - clear buffer

 :y  <l>        - yank (copy) line <l> to the copy buffer
 :x  <l>        - cut line <l> and store it in the copy buffer
 :p  <l>        - put (paste) previously copied line directly after <l>
 :i  <l> <txt>  - insert new text <txt> at line <l>. Old line will move down
 :r  <l> <txt>  - replace line <l> with text <txt>
 :I  <l> <txt>  - insert text at the beginning of line <l>
 :A  <l> <txt>  - append text after the end of line <l>

 :s <l> <w> <txt> - search/replace word or regex <w> in buffer or on line <l>

 :f <l>    - flood-fill entire buffer or line <l>
 :fi <l>   - indent entire buffer or line <l>
 :fd <l>   - de-indent entire buffer or line <l>

 :echo - turn echoing of the input on/off (helpful for some clients)

    Legend:
    <l> - line numbers, or range lstart:lend, e.g. '3:7'.
    <w> - one word or several enclosed in quotes.
    <txt> - longer string, usually not needed to be enclosed in quotes.
"""

_ERROR_LOADFUNC = \
"""
{error}

{rBuffer load function error. Could not load initial data.{n
"""

_ERROR_SAVEFUNC = \
"""
{error}

{rSave function returned an error. Buffer not saved.{n
"""

_ERROR_NO_SAVEFUNC = "{rNo save function defined. Buffer cannot be saved.{n"

_MSG_SAVE_NO_CHANGE = "No changes need saving"
_DEFAULT_NO_QUITFUNC = "Exited editor."

_ERROR_QUITFUNC = \
"""
{error}

{rQuit function gave an error. Skipping.{n
"""

_MSG_NO_UNDO = "Nothing to undo"
_MSG_NO_REDO = "Nothing to redo"
_MSG_UNDO = "Undid one step."
_MSG_REDO = "Redid one step."

#------------------------------------------------------------
#
# Handle yes/no quit question
#
#------------------------------------------------------------

class CmdSaveYesNo(Command):
    """
    Save the editor state on quit. This catches
    nomatches (defaults to Yes), and avoid saves only if
    command was given specifically as "no" or "n".
    """
    key = _CMD_NOMATCH
    aliases = _CMD_NOINPUT
    locks = "cmd:all()"
    help_cateogory = "LineEditor"

    def func(self):
        "Implement the yes/no choice."
        # this is only called from inside the lineeditor
        # so caller.ndb._lineditor must be set.

        self.caller.cmdset.remove(SaveYesNoCmdSet)
        if self.raw_string.strip().lower() in ("no", "n"):
            # answered no
            self.caller.msg(self.caller.ndb._lineeditor.quit())
        else:
            # answered yes (default)
            self.caller.ndb._lineeditor.save_buffer()
            self.caller.ndb._lineeditor.quit()


class SaveYesNoCmdSet(CmdSet):
    "Stores the yesno question"
    key = "quitsave_yesno"
    priority = 1
    mergetype = "Replace"

    def at_cmdset_creation(self):
        "at cmdset creation"
        self.add(CmdSaveYesNo())


#------------------------------------------------------------
#
# Editor commands
#
#------------------------------------------------------------

class CmdEditorBase(Command):
    """
    Base parent for editor commands
    """
    locks = "cmd:all()"
    help_entry = "LineEditor"

    code = None
    editor = None

    def parse(self):
        """
        Handles pre-parsing

        Editor commands are on the form
            :cmd [li] [w] [txt]

        Where all arguments are optional.
            li  - line number (int), starting from 1. This could also
                  be a range given as <l>:<l>.
            w   - word(s) (string), could be encased in quotes.
            txt - extra text (string), could be encased in quotes.
        """

        linebuffer = []
        if self.editor:
            linebuffer = self.editor.get_buffer().split("\n")
        nlines = len(linebuffer)

        # The regular expression will split the line by whitespaces,
        # stripping extra whitespaces, except if the text is
        # surrounded by single- or double quotes, in which case they
        # will be kept together and extra whitespace preserved. You
        # can input quotes on the line by alternating single and
        # double quotes.
        arglist = [part for part in _RE_GROUP.findall(self.args) if part]
        temp = []
        for arg in arglist:
            # we want to clean the quotes, but only one type,
            # in case we are nesting.
            if arg.startswith('"'):
                arg.strip('"')
            elif arg.startswith("'"):
                arg.strip("'")
            temp.append(arg)
        arglist = temp

        # A dumb split, without grouping quotes
        words = self.args.split()

        # current line number
        cline = nlines - 1

        # the first argument could also be a range of line numbers, on the
        # form <lstart>:<lend>. Either of the ends could be missing, to
        # mean start/end of buffer respectively.

        lstart, lend = cline, cline + 1
        linerange = False
        if arglist and ':' in arglist[0]:
            part1, part2 = arglist[0].split(':')
            if part1 and part1.isdigit():
                lstart = min(max(0, int(part1)) - 1, nlines)
                linerange = True
            if part2 and part2.isdigit():
                lend = min(lstart + 1, int(part2)) + 1
                linerange = True
        elif arglist and arglist[0].isdigit():
            lstart = min(max(0, int(arglist[0]) - 1), nlines)
            lend = lstart + 1
            linerange = True
        if linerange:
            arglist = arglist[1:]

        # nicer output formatting of the line range.
        lstr = ""
        if not linerange or lstart + 1 == lend:
            lstr = "line %i" % (lstart + 1)
        else:
            lstr = "lines %i-%i" % (lstart + 1, lend)

        # arg1 and arg2 is whatever arguments. Line numbers or -ranges are
        # never included here.
        args = " ".join(arglist)
        arg1, arg2 = "", ""
        if len(arglist) > 1:
            arg1, arg2 = arglist[0], " ".join(arglist[1:])
        else:
            arg1 = " ".join(arglist)

        # store for use in func()

        self.linebuffer = linebuffer
        self.nlines = nlines
        self.arglist = arglist
        self.cline = cline
        self.lstart = lstart
        self.lend = lend
        self.linerange = linerange
        self.lstr = lstr
        self.words = words
        self.args = args
        self.arg1 = arg1
        self.arg2 = arg2


class CmdLineInput(CmdEditorBase):
    """
    No command match - Inputs line of text into buffer.
    """
    key = _CMD_NOMATCH
    aliases = _CMD_NOINPUT

    def func(self):
        """
        Adds the line without any formatting changes.
        """
        editor = self.editor
        buf = editor.get_buffer()

        # add a line of text to buffer
        if not buf:
            buf = self.args
        else:
            buf = buf + "\n%s" % self.args
        self.editor.update_buffer(buf)
        if self.editor._echo_mode:
            # need to do it here or we will be off one line
            cline = len(self.editor.get_buffer().split('\n'))
            self.caller.msg("{b%02i|{n %s" % (cline, self.args))


class CmdEditorGroup(CmdEditorBase):
    """
    Commands for the editor
    """
    key = ":editor_command_group"
    aliases = [":","::", ":::", ":h", ":w", ":wq", ":q", ":q!", ":u", ":uu", ":UU",
               ":dd", ":dw", ":DD", ":y", ":x", ":p", ":i",
               ":r", ":I", ":A", ":s", ":S", ":f", ":fi", ":fd", ":echo"]
    arg_regex = r"\s.*?|$"

    def func(self):
        """
        This command handles all the in-editor :-style commands. Since
        each command is small and very limited, this makes for a more
        efficient presentation.
        """
        caller = self.caller
        editor = self.editor
        linebuffer = self.linebuffer
        lstart, lend = self.lstart, self.lend
        cmd = self.cmdstring
        echo_mode = self.editor._echo_mode

        if cmd == ":":
            # Echo buffer
            if self.linerange:
                buf = linebuffer[lstart:lend]
                editor.display_buffer(buf=buf, offset=lstart)
            else:
                editor.display_buffer()
        elif cmd == "::":
            # Echo buffer without the line numbers and syntax parsing
            if self.linerange:
                buf = linebuffer[lstart:lend]
                editor.display_buffer(buf=buf,
                                      offset=lstart,
                                      linenums=False, raw=True)
            else:
                editor.display_buffer(linenums=False, raw=True)
        elif cmd == ":::":
            # Insert single colon alone on a line
            editor.update_buffer(editor.buffer + "\n:")
            if echo_mode:
                caller.msg("Single ':' added to buffer.")
        elif cmd == ":h":
            # help entry
            editor.display_help()
        elif cmd == ":w":
            # save without quitting
            editor.save_buffer()
        elif cmd == ":wq":
            # save and quit
            editor.save_buffer()
            editor.quit()
        elif cmd == ":q":
            # quit. If not saved, will ask
            if self.editor._unsaved:
                caller.cmdset.add(SaveYesNoCmdSet)
                caller.msg("Save before quitting? {lcyes{lt[Y]{le/{lcno{ltN{le")
            else:
                editor.quit()
        elif cmd == ":q!":
            # force quit, not checking saving
            editor.quit()
        elif cmd == ":u":
            # undo
            editor.update_undo(-1)
        elif cmd == ":uu":
            # redo
            editor.update_undo(1)
        elif cmd == ":UU":
            # reset buffer
            editor.update_buffer(editor._pristine_buffer)
            caller.msg("Reverted all changes to the buffer back to original state.")
        elif cmd == ":dd":
            # :dd <l> - delete line <l>
            buf = linebuffer[:lstart] + linebuffer[lend:]
            editor.update_buffer(buf)
            caller.msg("Deleted %s." % (self.lstr))
        elif cmd == ":dw":
            # :dw <w> - delete word in entire buffer
            # :dw <l> <w> delete word only on line(s) <l>
            if not self.arg1:
                caller.msg("You must give a search word to delete.")
            else:
                if not self.linerange:
                    lstart = 0
                    lend = self.cline + 1
                    caller.msg("Removed %s for lines %i-%i." % (self.arg1, lstart + 1, lend + 1))
                else:
                    caller.msg("Removed %s for %s." % (self.arg1, self.lstr))
                sarea = "\n".join(linebuffer[lstart:lend])
                sarea = re.sub(r"%s" % self.arg1.strip("\'").strip('\"'), "", sarea, re.MULTILINE)
                buf = linebuffer[:lstart] + sarea.split("\n") + linebuffer[lend:]
                editor.update_buffer(buf)
        elif cmd == ":DD":
            # clear buffer
            editor.update_buffer("")
            caller.msg("Cleared %i lines from buffer." % self.nlines)
        elif cmd == ":y":
            # :y <l> - yank line(s) to copy buffer
            cbuf = linebuffer[lstart:lend]
            editor._copy_buffer = cbuf
            caller.msg("%s, %s yanked." % (self.lstr.capitalize(), cbuf))
        elif cmd == ":x":
            # :x <l> - cut line to copy buffer
            cbuf = linebuffer[lstart:lend]
            editor._copy_buffer = cbuf
            buf = linebuffer[:lstart] + linebuffer[lend:]
            editor.update_buffer(buf)
            caller.msg("%s, %s cut." % (self.lstr.capitalize(), cbuf))
        elif cmd == ":p":
            # :p <l> paste line(s) from copy buffer
            if not editor._copy_buffer:
                caller.msg("Copy buffer is empty.")
            else:
                buf = linebuffer[:lstart] + editor._copy_buffer + linebuffer[lstart:]
                editor.update_buffer(buf)
                caller.msg("Copied buffer %s to %s." % (editor._copy_buffer, self.lstr))
        elif cmd == ":i":
            # :i <l> <txt> - insert new line
            new_lines = self.args.split('\n')
            if not new_lines:
                caller.msg("You need to enter a new line and where to insert it.")
            else:
                buf = linebuffer[:lstart] + new_lines + linebuffer[lstart:]
                editor.update_buffer(buf)
                caller.msg("Inserted %i new line(s) at %s." % (len(new_lines), self.lstr))
        elif cmd == ":r":
            # :r <l> <txt> - replace lines
            new_lines = self.args.split('\n')
            if not new_lines:
                caller.msg("You need to enter a replacement string.")
            else:
                buf = linebuffer[:lstart] + new_lines + linebuffer[lend:]
                editor.update_buffer(buf)
                caller.msg("Replaced %i line(s) at %s." % (len(new_lines), self.lstr))
        elif cmd == ":I":
            # :I <l> <txt> - insert text at beginning of line(s) <l>
            if not self.args:
                caller.msg("You need to enter text to insert.")
            else:
                buf = linebuffer[:lstart] + ["%s%s" % (self.args, line) for line in linebuffer[lstart:lend]] + linebuffer[lend:]
                editor.update_buffer(buf)
                caller.msg("Inserted text at beginning of %s." % self.lstr)
        elif cmd == ":A":
            # :A <l> <txt> - append text after end of line(s)
            if not self.args:
                caller.msg("You need to enter text to append.")
            else:
                buf = linebuffer[:lstart] + ["%s%s" % (line, self.args) for line in linebuffer[lstart:lend]] + linebuffer[lend:]
                editor.update_buffer(buf)
                caller.msg("Appended text to end of %s." % self.lstr)
        elif cmd == ":s":
            # :s <li> <w> <txt> - search and replace words
            # in entire buffer or on certain lines
            if not self.arg1 or not self.arg2:
                caller.msg("You must give a search word and something to replace it with.")
            else:
                if not self.linerange:
                    lstart = 0
                    lend = self.cline + 1
                    caller.msg("Search-replaced %s -> %s for lines %i-%i." % (self.arg1, self.arg2, lstart + 1 , lend))
                else:
                    caller.msg("Search-replaced %s -> %s for %s." % (self.arg1, self.arg2, self.lstr))
                sarea = "\n".join(linebuffer[lstart:lend])

                regex = r"%s|^%s(?=\s)|(?<=\s)%s(?=\s)|^%s$|(?<=\s)%s$"
                regarg = self.arg1.strip("\'").strip('\"')
                if " " in regarg:
                    regarg = regarg.replace(" ", " +")
                sarea = re.sub(regex % (regarg, regarg, regarg, regarg, regarg), self.arg2.strip("\'").strip('\"'), sarea, re.MULTILINE)
                buf = linebuffer[:lstart] + sarea.split("\n") + linebuffer[lend:]
                editor.update_buffer(buf)
        elif cmd == ":f":
            # :f <l> flood-fill buffer or <l> lines of buffer.
            width = _DEFAULT_WIDTH
            if not self.linerange:
                lstart = 0
                lend = self.cline + 1
                caller.msg("Flood filled lines %i-%i." % (lstart + 1 , lend))
            else:
                caller.msg("Flood filled %s." % self.lstr)
            fbuf = "\n".join(linebuffer[lstart:lend])
            fbuf = fill(fbuf, width=width)
            buf = linebuffer[:lstart] + fbuf.split("\n") + linebuffer[lend:]
            editor.update_buffer(buf)
        elif cmd == ":fi":
            # :fi <l> indent buffer or lines <l> of buffer.
            indent = " " * 4
            if not self.linerange:
                lstart = 0
                lend = self.cline + 1
                caller.msg("Indented lines %i-%i." % (lstart + 1 , lend))
            else:
                caller.msg("Indented %s." % self.lstr)
            fbuf = [indent + line for line in linebuffer[lstart:lend]]
            buf = linebuffer[:lstart] + fbuf + linebuffer[lend:]
            editor.update_buffer(buf)
        elif cmd == ":fd":
            # :fi <l> indent buffer or lines <l> of buffer.
            if not self.linerange:
                lstart = 0
                lend = self.cline + 1
                caller.msg("Removed left margin (dedented) lines %i-%i." % (lstart + 1 , lend))
            else:
                caller.msg("Removed left margin (dedented) %s." % self.lstr)
            fbuf = "\n".join(linebuffer[lstart:lend])
            fbuf = dedent(fbuf)
            buf = linebuffer[:lstart] + fbuf.split("\n") + linebuffer[lend:]
            editor.update_buffer(buf)
        elif cmd == ":echo":
            # set echoing on/off
            editor._echo_mode = not editor._echo_mode
            caller.msg("Echo mode set to %s" % editor._echo_mode)


class EvEditorCmdSet(CmdSet):
    "CmdSet for the editor commands"
    key = "editorcmdset"
    mergetype = "Replace"

#------------------------------------------------------------
#
# Main Editor object
#
#------------------------------------------------------------

class EvEditor(object):
    """
    This defines a line editor object. It creates all relevant commands
    and tracks the current state of the buffer. It also cleans up after
    itself.

    """

    def __init__(self, caller, loadfunc=None, savefunc=None,
                 quitfunc=None, key=""):
        """
        Args:
            caller (Object): Who is using the editor.
            loadfunc (callable, optional): This will be called as
                `loadfunc(caller)` when the editor is first started. Its
                return will be used as the editor's starting buffer.
            savefunc (callable, optional): This will be called as
                `savefunc(caller, buffer)` when the save-command is given and
                is used to actually determine where/how result is saved.
                It should return `True` if save was successful and also
                handle any feedback to the user.
            quitfunc (callable, optional): This will optionally be
                called as `quitfunc(caller)` when the editor is
                exited. If defined, it should handle all wanted feedback
                to the user.
            quitfunc_args (tuple, optional): Optional tuple of arguments to
                supply to `quitfunc`.
            key (str, optional): An optional key for naming this
                session and make it unique from other editing sessions.

        """
        self._key = key
        self._caller = caller
        self._caller.ndb._lineeditor = self
        self._buffer = ""
        self._unsaved = False

        if loadfunc:
            self._loadfunc = loadfunc
        else:
            self._loadfunc = lambda caller: self._buffer
        self.load_buffer()
        if savefunc:
            self._savefunc = savefunc
        else:
            self._savefunc = lambda caller: caller.msg(_ERROR_NO_SAVEFUNC)
        if quitfunc:
            self._quitfunc = quitfunc
        else:
            self._quitfunc = lambda caller: caller.msg(_DEFAULT_NO_QUITFUNC)

        # Create the commands we need
        cmd1 = CmdLineInput()
        cmd1.editor = self
        cmd1.obj = self
        cmd2 = CmdEditorGroup()
        cmd2.obj = self
        cmd2.editor = self
        # Populate cmdset and add it to caller
        editor_cmdset = EvEditorCmdSet()
        editor_cmdset.add(cmd1)
        editor_cmdset.add(cmd2)
        self._caller.cmdset.add(editor_cmdset)

        # store the original version
        self._pristine_buffer = self._buffer
        self._sep = "-"

        # undo operation buffer
        self._undo_buffer = [self._buffer]
        self._undo_pos = 0
        self._undo_max = 20

        # copy buffer
        self._copy_buffer = []

        # echo inserted text back to caller
        self._echo_mode = True

        # show the buffer ui
        self.display_buffer()

    def load_buffer(self):
        """
        Load the buffer using the load function hook.
        """
        try:
            self._buffer = self._loadfunc(self._caller)
        except Exception as e:
            self._caller.msg(_ERROR_LOADFUNC.format(error=e))

    def get_buffer(self):
        """
        Return:
            buffer (str): The current buffer.

        """
        return self._buffer

    def update_buffer(self, buf):
        """
        This should be called when the buffer has been changed
        somehow.  It will handle unsaved flag and undo updating.

        Args:
            buf (str): The text to update the buffer with.

        """
        if is_iter(buf):
            buf = "\n".join(buf)

        if buf != self._buffer:
            self._buffer = buf
            self.update_undo()
            self._unsaved = True

    def quit(self):
        """
        Cleanly exit the editor.

        """
        try:
            self._quitfunc(self._caller)
        except Exception as e:
            self._caller.msg(_ERROR_QUITFUNC.format(error=e))
        del self._caller.ndb._lineeditor
        self._caller.cmdset.remove(EvEditorCmdSet)

    def save_buffer(self):
        """
        Saves the content of the buffer. The 'quitting' argument is a bool
        indicating whether or not the editor intends to exit after saving.

        """
        if self._unsaved:
            try:
                if self._savefunc(self._caller, self._buffer):
                    # Save codes should return a true value to indicate
                    # save worked. The saving function is responsible for
                    # any status messages.
                    self._unsaved = False
            except Exception as e:
                self._caller.msg(_ERROR_SAVEFUNC.format(error=e))
        else:
            self._caller.msg(_MSG_SAVE_NO_CHANGE)

    def update_undo(self, step=None):
        """
        This updates the undo position.

        Args:
            step (int, optional): The amount of steps
                to progress the undo position to. This
                may be a negative value for undo and
                a positive value for redo.

        """
        if step and step < 0:
            # undo
            if self._undo_pos <= 0:
                self._caller.msg(_MSG_NO_UNDO)
            else:
                self._undo_pos = max(0, self._undo_pos + step)
                self._buffer = self._undo_buffer[self._undo_pos]
                self._caller.msg(_MSG_UNDO)
        elif step and step > 0:
            # redo
            if self._undo_pos >= len(self._undo_buffer) - 1 or self._undo_pos + 1 >= self._undo_max:
                self._caller.msg(_MSG_NO_REDO)
            else:
                self._undo_pos = min(self._undo_pos + step, min(len(self._undo_buffer), self._undo_max) - 1)
                self._buffer = self._undo_buffer[self._undo_pos]
                self._caller.msg(_MSG_REDO)
        if not self._undo_buffer or (self._undo_buffer and self._buffer != self._undo_buffer[self._undo_pos]):
            # save undo state
            self._undo_buffer = self._undo_buffer[:self._undo_pos + 1] + [self._buffer]
            self._undo_pos = len(self._undo_buffer) - 1

    def display_buffer(self, buf=None, offset=0, linenums=True, raw=False):
        """
        This displays the line editor buffer, or selected parts of it.

        Args:
            buf (str, optional): The buffer or part of buffer to display.
            offset (int, optional): If `buf` is set and is not the full buffer,
                `offset` should define the actual starting line number, to
                get the linenum display right.
            linenums (bool, optional): Show line numbers in buffer.
            raw (bool, optional): Tell protocol to not parse
                formatting information.

        """
        if buf == None:
            buf = self._buffer
        if is_iter(buf):
            buf = "\n".join(buf)

        lines = buf.split('\n')
        nlines = len(lines)
        nwords = len(buf.split())
        nchars = len(buf)

        sep = self._sep
        header = "{n" + sep * 10 + "Line Editor [%s]" % self._key + sep * (_DEFAULT_WIDTH-25-len(self._key))
        footer = "{n" + sep * 10 + "[l:%02i w:%03i c:%04i]" % (nlines, nwords, nchars) \
                    + sep * 12 + "(:h for help)" + sep * 23
        if linenums:
            main = "\n".join("{b%02i|{n %s" % (iline + 1 + offset, line) for iline, line in enumerate(lines))
        else:
            main = "\n".join(lines)
        string = "%s\n%s\n%s" % (header, main, footer)
        self._caller.msg(string, raw=raw)

    def display_help(self):
        """
        Shows the help entry for the editor.

        """
        string = self._sep * _DEFAULT_WIDTH + _HELP_TEXT + self._sep * _DEFAULT_WIDTH
        self._caller.msg(string)