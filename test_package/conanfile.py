import os

from conans import ConanFile, CMake, tools


class TestVerilatorConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake",

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        with tools.run_environment(self):
            self.run("verilator --version")
        self.run("bin/blinky")
