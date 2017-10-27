#!/bin/env python

from html.parser import HTMLParser
import os
import subprocess
import sys

output_file = 'codenarc-output.html'
output = subprocess.run(
    ["/usr/bin/codenarc", "-rulesetfiles=ruleset.groovy",
     "-report=html:%s" % output_file, "-includes=**/Jenkinsfile"],
    stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
sys.stdout.buffer.write(output.stdout)


# CodeNarc doesn't fail on compilation errors (?)
if 'Compilation failed' in str(output.stdout):
    print("Error when compiling files!")
    sys.exit(1)

print("Return code: %d" % output.returncode)

if output.returncode != 0:
    sys.exit(output.retcode)
if not os.path.exists(output_file):
    print("Error: %s was not generated, aborting!" % output_file)
    sys.exit(1)

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


parser = CodeNarcHTMLParser()
with open(output_file) as f:
    parser.feed(f.read())

if parser.violating_files is None:
    print("Error parsing CodeNarc output!")
    sys.exit(1)

if parser.violating_files > 0:
    print("Error: %d files with violations. See %s for details."
          % (parser.violating_files, output_file))
    sys.exit(1)

print("No violations detected!")
sys.exit(0) 
