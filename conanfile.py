from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import platform


class VerilatorConan(ConanFile):
    name = 'verilator'
    version = '4.004'
    license = 'GPLv3'
    url = 'https://github.com/madebr/conan-verilator'
    description = 'Verilator compiles synthesizable Verilog and Synthesis assertions into single- or multithreaded C++ or SystemC code'
    settings = 'os'
    options = {}
    default_options = {}
    generators = ()
    _source_subfolder = 'source_subfolder'

    def source(self):
        url = 'https://www.veripool.org/ftp/verilator-{}.tgz'.format(self.version)
        tools.get(url)
        extracted_dir = '{}-{}'.format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def build_requirements(self):
        if platform.system() == 'Windows':
            self.build_requires.add('winflexbison/2.5.16@bincrafters/stable')
        else:
            self.build_requires.add('flex/2.6.4@bincrafters/stable')
            self.build_requires.add('bison/3.0.4@bincrafters/stable')

    def get_auto_tools(self):
        autoTools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        return autoTools

    def build(self):
        with tools.chdir(self.build_folder):
            autoTools = self.get_auto_tools()
            autoTools.configure(configure_dir=os.path.join(self.source_folder, self._source_subfolder))
            autoTools.make()

    def package(self):
        self.copy(pattern='COPYING', dst='licenses', src=self._source_subfolder)
        with tools.chdir(self.build_folder):
            autoTools = self.get_auto_tools()
            autoTools.install()

    def package_info(self):
        self.cpp_info.bindirs = ['bin']
        self.cpp_info.includedirs = ['share/verilator/include']
