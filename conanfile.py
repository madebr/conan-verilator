from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os
import platform
import shutil


class VerilatorConan(ConanFile):
    name = "verilator"
    version = "4.010"
    license = "GPL-3.0"
    url = "https://github.com/bincrafters/conan-verilator"
    homepage = "https://www.veripool.org/wiki/verilator"
    description = "Verilator compiles synthesizable Verilog and Synthesis assertions into single- or multithreaded C++ or SystemC code"
    topics = ("conan", "verilog", "HDL", "EDA", "simulator", "hardware", "fpga", "asic")
    author = 'bincrafters <bincrafters@gmail.com>'

    settings = "os_build", "arch_build"
    _source_subfolder = "sources"

    def source(self):
        url = "https://www.veripool.org/ftp/verilator-{}.tgz".format(self.version)
        tools.get(url, sha256="5651748fe28e373ebf7a6364f5e7935ec9b39d29671f683f366e99d5e157d571")
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)
        lines = (
            "CFLAGS=-I${includedir}",
            "CPPFLAGS=-I${includedir}",
            "CXXFLAGS=-I${includedir}",
            "LDFLAGS=-L${libdir}"
        )
        conf_file = os.path.join(self.source_folder, self._source_subfolder, "configure")
        for line in lines:
            tools.replace_in_file(conf_file, line, "#{}".format(line))
        os.remove(os.path.join(self.source_folder, self._source_subfolder, "src", "config_build.h"))

    def build_requirements(self):
        if platform.system() == "Windows":
            self.build_requires("winflexbison/2.5.16@bincrafters/stable")
            self.build_requires("msys2_installer/20161025@bincrafters/stable")
        else:
            self.build_requires("flex/2.6.4@bincrafters/stable")
            self.build_requires("bison/3.0.4@bincrafters/stable")

    def imports(self):
        imports_folder = os.path.join(self.imports_folder, "imports")
        os.mkdir(imports_folder)
        if platform.system() == "Windows":
            shutil.copy(os.path.join(self.deps_cpp_info["winflexbison"].bin_paths[0], "win_bison.exe"),
                        os.path.join(imports_folder, "bison.exe"))
            shutil.copy(os.path.join(self.deps_cpp_info["winflexbison"].bin_paths[0], "win_flex.exe"),
                        os.path.join(imports_folder, "flex.exe"))

    def _get_auto_tools(self):
        autoTools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        return autoTools

    def build(self):
        with tools.environment_append({"PATH": [os.path.join(self.build_folder, "imports")]}):
            with tools.chdir(self.build_folder):
                autoTools = self._get_auto_tools()
                if platform.system() != "Windows":
                    if self.settings.arch_build == "x86":
                        autoTools.flags.append("-m32")
                    elif self.settings.arch_build == "x86_64":
                        autoTools.flags.append("-m64")
                    else:
                        raise ConanInvalidConfiguration("unknown arch_build: {}".format(str(self.settings.arch_build)))
                autoTools.configure(configure_dir=os.path.join(self.source_folder, self._source_subfolder))
                autoTools.make()

    def package(self):
        with tools.chdir(self.build_folder):
            autoTools = self._get_auto_tools()
            autoTools.install()
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        shutil.rmtree(os.path.join(self.package_folder, "share/verilator/examples"))
        for f in glob.glob(os.path.join(self.package_folder, "bin", "*dbg*")):
            os.remove(f)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = [os.path.join(self.package_folder, "share/verilator/include")]
        self.user_info.VERILATOR_ROOT = self.package_folder
        self.user_info.VERILATOR_ROOT_INCLUDE = os.path.join(self.package_folder, "share/verilator/include")
