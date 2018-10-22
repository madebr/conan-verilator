from conans import ConanFile, AutoToolsBuildEnvironment, tools
import glob
import os
import platform
import shutil


class VerilatorConan(ConanFile):
    name = "verilator"
    version = "4.006"
    license = "GPL-3.0"
    url = "https://github.com/madebr/conan-verilator"
    description = "Verilator compiles synthesizable Verilog and Synthesis assertions into single- or multithreaded C++ or SystemC code"
    settings = "os", "compiler", "build_type", "arch"
    _source_subfolder = "sources"

    def source(self):
        url = "https://www.veripool.org/ftp/verilator-{}.tgz".format(self.version)
        tools.get(url, sha256="31dc2d2dcdfa09e935e9622169005e34262471740e00c4dde0941267e75dde6e")
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
        from conans.client.tools.oss import get_cross_building_settings

        with tools.environment_append({"PATH": [os.path.join(self.build_folder, "imports")]}):
            with tools.chdir(self.build_folder):
                autoTools = self._get_auto_tools()
                if self.settings.os != "Windows":
                    _, _, _, host_arch = get_cross_building_settings(self.settings)
                    if host_arch == "x86":
                        autoTools.flags.append("-m32")
                    elif host_arch == "x86_64":
                        autoTools.flags.append("-m64")
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
