'''
Commands and utilities for pre.py scripts
'''

import sys
import os
import shutil
from argparse import ArgumentParser
from dotnet import CSharpProject, CSharpProjFile
from shared import const
from shared.util import helixpayload
from shared.codefixes import replace_line, insert_after
from performance.common import get_packages_directory, get_repo_root_path

BUILD = 'build'
PUBLISH = 'publish'
BACKUP = 'backup'
DEBUG = 'Debug'
RELEASE = 'Release'

OPERATIONS = (BUILD,
              PUBLISH,
              BACKUP
             )

class PreCommands:
    '''
    Handles building and publishing
    '''

    def __init__(self):
        self.project: CSharpProject
        self.projectfile: CSharpProjFile
        parser = ArgumentParser()
        subparsers = parser.add_subparsers(title='Operations', 
                                           description='Common preperation steps for perf tests.',
                                           required=True,
                                           dest='operation')

        build_parser = subparsers.add_parser(BUILD, help='Builds the project')
        self.add_common_arguments(build_parser)

        publish_parser = subparsers.add_parser(PUBLISH, help='Publishes the project')
        self.add_common_arguments(publish_parser)

        backup_parser = subparsers.add_parser(BACKUP, help='Backs up the project to tmp folder')
        self.add_common_arguments(backup_parser)

        args = parser.parse_args()
        self.configuration = args.configuration
        self.operation = args.operation
        self.framework = args.framework
        self.runtime = args.runtime
        self.msbuild = args.msbuild

    def new(self,
            template: str,
            output_dir: str,
            bin_dir: str,
            exename: str,
            working_directory: str,
            language: str = None):
        'makes a new app with the given template'
        self.project = CSharpProject.new(template=template,
                                 output_dir=output_dir,
                                 bin_dir=bin_dir,
                                 exename=exename,
                                 working_directory=working_directory,
                                 force=True,
                                 verbose=True,
                                 target_framework_moniker=self.framework,
                                 language=language)
        return self

    def add_common_arguments(self, parser: ArgumentParser):
        "Options that are common across many 'dotnet' commands"
        parser.add_argument('-c', '--configuration',
                            dest='configuration',
                            choices=[DEBUG, RELEASE],
                            metavar='config')
        parser.add_argument('-f', '--framework',
                            dest='framework',
                            metavar='framework')
        parser.add_argument('-r', '--runtime',
                            dest='runtime',
                            metavar='runtime')
        parser.add_argument('--msbuild',
                            help='Flags passed through to msbuild',
                            dest='msbuild',
                            metavar='/p:Foo=Bar;/p:Baz=Blee;...')
        parser.set_defaults(configuration=RELEASE)

    def existing(self, projectdir: str, projectfile: str):
        'create a project from existing project file'

        # copy from projectdir to appdir
        if os.path.isdir(const.APPDIR):
            shutil.rmtree(const.APPDIR)
        shutil.copytree(projectdir, const.APPDIR)
        csproj = CSharpProjFile(os.path.join(const.APPDIR, projectfile), sys.path[0])
        self.project = CSharpProject(csproj, const.BINDIR)
        self._updateframework(csproj.file_name)
        return self

    def execute(self):
        'Parses args and runs precommands'
        if self.operation == BUILD:
            self._restore()
            self._build(configuration=self.configuration, framework=self.framework)
        if self.operation == PUBLISH:
            self._restore()
            self._publish(self.configuration)
        if self.operation == BACKUP:
            self._backup()

    def add_startup_logging(self, file: str, line: str):
        self.add_event_source(file, line, "PerfLabGenericEventSource.Log.Startup();")

    def add_event_source(self, file: str, line: str, trace_statement: str):
        '''
        Adds a copy of the event source to the project and inserts the correct call
        file: relative path to the root of the project (where the project file lives)
        line: Exact line to insert trace statement after
        trace_statement: Statement to insert
        '''

        projpath = os.path.dirname(self.project.csproj_file)
        staticpath = os.path.join(get_repo_root_path(), "src", "scenarios", "staticdeps")
        if helixpayload():
            staticpath = os.path.join(helixpayload(), "staticdeps")
        shutil.copyfile(os.path.join(staticpath, "PerfLab.cs"), os.path.join(projpath, "PerfLab.cs"))
        filepath = os.path.join(projpath, file)
        insert_after(filepath, line, trace_statement)
        

    def _backup(self):
        'make a temp copy of the asset'
        if os.path.isdir(const.TMPDIR):
            shutil.rmtree(const.TMPDIR)
        shutil.copytree(const.APPDIR, const.TMPDIR)

    def _updateframework(self, projectfile: str):
        if self.framework:
            replace_line(projectfile, "$FRAMEWORK", self.framework)

    def _publish(self, configuration: str, framework: str = None):
        self.project.publish(configuration=configuration,
                             output_dir=const.PUBDIR, 
                             verbose=True,
                             packages_path=get_packages_directory(),
                             target_framework_moniker=framework
                             )

    def _restore(self):
        self.project.restore(packages_path=get_packages_directory(), verbose=True)

    def _build(self, configuration: str, framework: str = None):
        self.project.build(configuration=configuration,
                               verbose=True,
                               packages_path=get_packages_directory(),
                               target_framework_monikers=framework,
                               output_to_bindir=True)