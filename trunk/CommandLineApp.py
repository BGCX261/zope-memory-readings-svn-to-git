#!/usr/bin/env python
#
# Copyright 2007 Doug Hellmann.
#
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of Doug
# Hellmann not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# DOUG HELLMANN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT SHALL DOUG HELLMANN BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

"""Base class for building command line applications.

  The CommandLineApp class makes creating command line applications as
  simple as defining callbacks to handle options when they appear in
  'sys.argv'.
"""

__module_id__ = "$Id: CommandLineApp.py 1322 2008-03-10 12:53:21Z dhellmann $"

#
# Import system modules
#
import getopt
import inspect
import os
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import sys
import textwrap

#
# Import Local modules
#

#
# Module
#

class OptionDef(object):
    """Definition for a command line option.

    Attributes:

      method_name - The name of the option handler method.
      option_name - The name of the option.
      switch      - Switch to be used on the command line.
      arg_name    - The name of the argument to the option handler.
      is_variable - Is the argument expected to be a sequence?
      default     - The default value of the option handler argument.
      help        - Help text for the option.
      is_long     - Is the option a long value (--) or short (-)?
    """

    # Option handler method names start with this value
    OPTION_HANDLER_PREFIX = 'optionHandler_'

    # For *args arguments to option handlers, how to split the argument values
    SPLIT_PARAM_CHAR = ','
    
    def __init__(self, methodName, method):
        self.method_name = methodName
        self.option_name = methodName[len(self.OPTION_HANDLER_PREFIX):]
        self.is_long = len(self.option_name) > 1

        self.switch_base = self.option_name.replace('_', '-')
        if len(self.switch_base) == 1:
            self.switch = '-' + self.switch_base
        else:
            self.switch = '--' + self.switch_base

        argspec = inspect.getargspec(method)

        self.is_variable = False
        args = argspec[0]
        if len(args) > 1:
            self.arg_name = args[-1]
        elif argspec[1]:
            self.arg_name = argspec[1]
            self.is_variable = True
        else:
            self.arg_name = None

        if argspec[3]:
            self.default = argspec[3][0]
        else:
            self.default = None

        self.help = inspect.getdoc(method)
        return

    def getSwitchText(self):
        """Return the description of the option switch.

        For example: --switch=arg or -s arg or --switch=arg[,arg]
        """
        parts = [ self.switch ]
        if self.arg_name:
            if self.is_long:
                parts.append('=')
            else:
                parts.append(' ')
            parts.append(self.arg_name)
            if self.is_variable:
                parts.append('[%s%s...]' % (self.SPLIT_PARAM_CHAR, self.arg_name))
        return ''.join(parts)


    def invoke(self, app, arg):
        """Invoke the option handler.
        """
        method = getattr(app, self.method_name)
        if self.arg_name:
            if self.is_variable:
                opt_args = arg.split(self.SPLIT_PARAM_CHAR)
                method(*opt_args)
            else:
                method(arg)
        else:
            method()
        return


class CommandLineApp(object):
    """Base class for building command line applications.
    
    Define a docstring for the class to explain what the program does.

    Include descriptions of the command arguments in the docstring for
    main().

    When the EXAMPLES_DESCRIPTION class attribute is not empty, it
    will be printed last in the help message when the user asks for
    help.
    """

    EXAMPLES_DESCRIPTION = ''

    # If true, always ends run() with sys.exit()
    force_exit = True

    # The name of this application
    _app_name = os.path.basename(sys.argv[0])

    _app_version = None

    def __init__(self, commandLineOptions=sys.argv[1:]):
        "Initialize CommandLineApp."
        self.command_line_options = commandLineOptions
        self.beforeOptionsHook()
        self.supported_options = self.scanForOptions()
        self.afterOptionsHook()
        return
        
    def beforeOptionsHook(self):
        """Hook to initialize the app before the options are processed.
        
        Overriding __init__() requires special handling to make sure the
        arguments are still passed to the base class.  Override this method
        instead to create local attributes or do other initialization before
        the command line options are processed.
        """
        return
    
    def afterOptionsHook(self):
        """Hook to initialize the app after the options are processed.
        
        Overriding __init__() requires special handling to make sure the
        arguments are still passed to the base class.  Override this method
        instead to create local attributes or do other initialization after
        the command line options are processed.
        """
        return

    def main(self, *args):
        """Main body of your application.

        This is the main portion of the app, and is run after all of
        the arguments are processed.  Override this method to implment
        the primary processing section of your application.
        """
        pass

    def handleInterrupt(self):
        """Called when the program is interrupted via Control-C
        or SIGINT.  Returns exit code.
        """
        sys.stderr.write('Canceled by user.\n')
        return 1

    def handleMainException(self, err):
        """Invoked when there is an error in the main() method.
        """
        if self.debugging:
            import traceback
            traceback.print_exc()
        else:
            self.errorMessage(str(err))
        return 1

    ## HELP

    def showHelp(self, errorMessage=None):
        "Display help message when error occurs."
        print
        if self._app_version:
            print '%s version %s' % (self._app_name, self._app_version)
        else:
            print self._app_name
        print
            
        #
        # If they made a syntax mistake, just
        # show them how to use the program.  Otherwise,
        # show the full help message.
        #
        if errorMessage:
            print ''
            print 'ERROR: ', errorMessage
            print ''
            print ''
            print '%s\n' % self._app_name
            print ''

        txt = self.getSimpleSyntaxHelpString()
        print txt
        print 'For more details, use --help.'
        print
        return

    def showVerboseHelp(self):
        "Display the full help text for the command."
        txt = self.getVerboseSyntaxHelpString()
        print txt
        return

    ## STATUS MESSAGES

    def _statusMessage(self, msg, output):
        if isinstance(msg, unicode):
            to_print = msg.encode('ascii', 'replace')
        else:
            to_print = unicode(msg, 'utf-8').encode('ascii', 'replace')
        output.write(to_print)
        return

    def statusMessage(self, msg='', verbose_level=1, error=False, newline=True):
        """Print a status message to output.
        
        Arguments
        
            msg=''            -- The status message string to be printed.
            
            verbose_level=1   -- The verbose level to use.  The message
                              will only be printed if the current verbose
                              level is >= this number.
                              
            error=False       -- If true, the message is considered an error and
                              printed as such.

            newline=True      -- If true, print a newline after the message.
                              
        """
        if self.verbose_level >= verbose_level:
            if error:
                output = sys.stderr
            else:
                output = sys.stdout
            self._statusMessage(msg, output)
            if newline:
                output.write('\n')
            # some log mechanisms don't have a flush method
            if hasattr(output, 'flush'):
                output.flush()
        return
    
    def errorMessage(self, msg=''):
        'Print a message as an error.'
        self.statusMessage('ERROR: %s\n' % msg, verbose_level=0, error=True)
        return

    ## DEFAULT OPTIONS

    debugging = False
    def optionHandler_debug(self):
        "Set debug mode to see tracebacks."
        self.debugging = True
        return

    _run_main = True
    def optionHandler_h(self):
        "Displays abbreviated help message."
        self.showHelp()
        self._run_main = False
        return

    def optionHandler_help(self):
        "Displays verbose help message."
        self.showVerboseHelp()
        self._run_main = False
        return

    def optionHandler_quiet(self):
        'Turn on quiet mode.'
        self.verbose_level = 0
        return
                
    verbose_level = 1
    def optionHandler_v(self):
        """Increment the verbose level.
        Higher levels are more verbose.
        The default is 1.
        """
        self.verbose_level = self.verbose_level + 1
        self.statusMessage('New verbose level is %d' % self.verbose_level,
                           3)
        return

    def optionHandler_verbose(self, level=1):
        """Set the verbose level.
        """
        self.verbose_level = int(level)
        self.statusMessage('New verbose level is %d' % self.verbose_level,
                           3)
        return

    ## INTERNALS (Subclasses should not need to override these methods)

    def run(self):
        """Entry point.

        Process options and execute callback functions as needed.
        This method should not need to be overridden, if the main()
        method is defined.
        """
        # Process the options supported and given
        options = {}
        for info in self.supported_options:
            options[ info.switch ] = info
        parsed_options, remaining_args = self.callGetopt(self.command_line_options,
                                                         self.supported_options)
        exit_code = 0
        try:
            for switch, option_value in parsed_options:
                opt_def = options[switch]
                opt_def.invoke(self, option_value)

            # Perform the primary action for this application,
            # unless one of the options has disabled it.
            if self._run_main:
                main_args = tuple(remaining_args)

                # We could just call main() and catch a TypeError,
                # but that would not let us differentiate between
                # application errors and a case where the user
                # has not passed us enough arguments.  So, we check
                # the argument count ourself.
                num_args_ok = False
                argspec = inspect.getargspec(self.main)
                expected_arg_count = len(argspec[0]) - 1

                if argspec[1] is not None:
                    num_args_ok = True
                    if len(argspec[0]) > 1:
                        num_args_ok = (len(main_args) >= expected_arg_count)
                elif len(main_args) == expected_arg_count:
                    num_args_ok = True

                if num_args_ok:
                    exit_code = self.main(*main_args)
                else:
                    self.showHelp('Incorrect arguments.')
                    exit_code = 1

        except KeyboardInterrupt:
            exit_code = self.handleInterrupt()

        except SystemExit, msg:
            exit_code = msg.args[0]

        except Exception, err:
            exit_code = self.handleMainException(err)
            
        if self.force_exit:
            sys.exit(exit_code)
        return exit_code
        
    def scanForOptions(self):
        "Scan through the inheritence hierarchy to find option handlers."
        options = []

        methods = inspect.getmembers(self.__class__, inspect.ismethod)
        for method_name, method in methods:
            if method_name.startswith(OptionDef.OPTION_HANDLER_PREFIX):
                options.append(OptionDef(method_name, method))

        return options

    def callGetopt(self, commandLineOptions, supportedOptions):
        "Parse the command line options."
        short_options = []
        long_options = []
        for o in supportedOptions:
            if len(o.option_name) == 1:
                short_options.append(o.option_name)
                if o.arg_name:
                    short_options.append(':')
            elif o.arg_name:
                long_options.append('%s=' % o.switch_base)
            else:
                long_options.append(o.switch_base)

        short_option_string = ''.join(short_options)

        try:
            parsed_options, remaining_args = getopt.getopt(
                commandLineOptions,
                short_option_string,
                long_options)
        except getopt.error, message:
            self.showHelp(message)
            if self.force_exit:
                sys.exit(1)
            raise
        return (parsed_options, remaining_args)

    def _groupOptionAliases(self):
        """Return a sequence of tuples containing
        (option_names, option_defs)
        """
        # Figure out which options are aliases
        option_aliases = {}
        for option in self.supported_options:
            method = getattr(self, option.method_name)
            existing_aliases = option_aliases.setdefault(method, [])
            existing_aliases.append(option)

        # Sort the groups in order
        grouped_options = []
        for options in option_aliases.values():
            names = [ o.option_name for o in options ]
            grouped_options.append( (names, options) )
        grouped_options.sort()
        return grouped_options

    def _getOptionIdentifierText(self, options):
        """Return the option identifier text.

        For example:

          -h
          -v, --verbose
          -f bar, --foo bar
        """
        option_texts = []
        for option in options:
            option_texts.append(option.getSwitchText())
        return ', '.join(option_texts)

    def getArgumentsSyntaxString(self):
        """Look at the arguments to main to see what the program accepts,
        and build a syntax string explaining how to pass those arguments.
        """
        syntax_parts = []
        argspec = inspect.getargspec(self.main)
        args = argspec[0]
        if len(args) > 1:
            for arg in args[1:]:
                syntax_parts.append(arg)
        if argspec[1]:
            syntax_parts.append(argspec[1])
            syntax_parts.append('[' + argspec[1] + '...]')
        syntax = ' '.join(syntax_parts)
        return syntax
            
    def getSimpleSyntaxHelpString(self):    
        """Return syntax statement.
        
        Return a simplified form of help including only the 
        syntax of the command.
        """
        buffer = StringIO()
        
        # Show the name of the command and basic syntax.
        buffer.write('%s [<options>] %s\n\n' % \
                         (self._app_name, self.getArgumentsSyntaxString())
                     )

        grouped_options = self._groupOptionAliases()

        # Assemble the text for the options
        for names, options in grouped_options:
            buffer.write('    %s\n' % self._getOptionIdentifierText(options))
            
        return buffer.getvalue()

    def _formatHelpText(self, text, prefix):
        if not text:
            return ''
        buffer = StringIO()
        text = textwrap.dedent(text)
        for para in text.split('\n\n'):
            formatted_para = textwrap.fill(para, 
                                           initial_indent=prefix, 
                                           subsequent_indent=prefix,
                                           )
            buffer.write(formatted_para)
            buffer.write('\n\n')
        return buffer.getvalue()

    def getVerboseSyntaxHelpString(self):
        """Return the full description of the options and arguments.

        Show a full description of the options and arguments to the
        command in something like UNIX man page format. This includes
        
          - a description of each option and argument, taken from the
                __doc__ string for the optionHandler method for
                the option
                
          - a description of what additional arguments will be processed,
                taken from the arguments to main()
                
        """
        buffer = StringIO()

        class_help_text = self._formatHelpText(inspect.getdoc(self.__class__),
                                               '')
        buffer.write(class_help_text)

        buffer.write('\nSYNTAX:\n\n  ')
        buffer.write(self.getSimpleSyntaxHelpString())

        main_help_text = self._formatHelpText(inspect.getdoc(self.main), '    ')
        if main_help_text:
            buffer.write('\n\nARGUMENTS:\n\n')
            buffer.write(main_help_text)

        buffer.write('\nOPTIONS:\n\n')

        grouped_options = self._groupOptionAliases()
            
        # Describe all options, grouping aliases together
        for names, options in grouped_options:
            buffer.write('    %s\n' % self._getOptionIdentifierText(options))

            help = self._formatHelpText(options[0].help, '        ')
            buffer.write(help)
            
        if self.EXAMPLES_DESCRIPTION:
            buffer.write('EXAMPLES:\n\n')
            buffer.write(self.EXAMPLES_DESCRIPTION)
        return buffer.getvalue()


if __name__ == '__main__':
    CommandLineApp().run()
