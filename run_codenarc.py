#!/bin/env python

import argparse
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
    print("hello, it's me!") 

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'codenarc_args', nargs='*',
        default=['-includes=**/Jenkinsfile'],
        help='Extra arguments to pass to CodeNarc, such as -includes=')
    parsed_args = parser.parse_args()

    output_file = 'codenarc-output.html'
    args = ["/usr/bin/codenarc", "-rulesetfiles=ruleset.groovy",
            "-report=html:%s" % output_file] + parsed_args.codenarc_args

    return 0
    output = subprocess.run(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    sys.stdout.buffer.write(output.stdout)


    # CodeNarc doesn't fail on compilation errors (?)
    if 'Compilation failed' in str(output.stdout):
        print("Error when compiling files!")
        return 1

    print("Return code: %d" % output.returncode)

    if output.returncode != 0:
        return output.retcode
    if not os.path.exists(output_file):
        print("Error: %s was not generated, aborting!" % output_file)
        return 1

    parser = CodeNarcHTMLParser()
    with open(output_file) as f:
        parser.feed(f.read())

    if parser.violating_files is None:
        print("Error parsing CodeNarc output!")
        return 1

    if parser.violating_files > 0:
        print("Error: %d files with violations. See %s for details."
              % (parser.violating_files, output_file))
        return 1

    print("No violations detected!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
