#!/bin/env python

import os
import subprocess
import sys

from html.parser import HTMLParser

class CodeNarcHTMLParser(HTMLParser):
    saw_all_packages = False
    my_offset = 0
    current_tag = None
    violating_files = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag

    def handle_data(self, data):
        if self.violating_files is not None:
            return
        if self.current_tag != 'td':
            return
        if self.saw_all_packages:
            self.my_offset = self.my_offset + 1
        elif data == 'All Packages':
            self.saw_all_packages = True
        if self.my_offset == 2:
            if data == '-':
                data = "0"
            self.violating_files = int(data)


def main():
    parsed_args = sys.argv[1:]
    parsed_args = parsed_args or ['-includes=**/Jenkinsfile']

    output_file = 'codenarc-output.html'
    args = ["/usr/bin/codenarc", "-rulesetfiles=ruleset.groovy",
            "-report=html:%s" % output_file] + parsed_args

    output = subprocess.run(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    sys.stdout.buffer.write(output.stdout)

    # CodeNarc doesn't fail on compilation errors (?)
    if 'Compilation failed' in str(output.stdout):
        print("Error when compiling files!")
        return 1

    print("Return code: %d" % output.returncode)

    if output.returncode != 0:
        return output.returncode
    if not os.path.exists(output_file):
        print("Error: %s was not generated, aborting!" % output_file)
        return 1

    parser = CodeNarcHTMLParser()
    with open(output_file) as f:
        parser.feed(f.read())

    if parser.violating_files is None:
        print("Error parsing CodeNarc output!")
        return 1

    error_file = 'codenarc-output-errors.html'
    if parser.violating_files > 0:
        print('Moving %s to %s.' % (output_file, error_file))
        os.rename(output_file, error_file)
        print("Error: %d files with violations. See %s for details."
              % (parser.violating_files, error_file))
        return 1

    print("No violations detected!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
