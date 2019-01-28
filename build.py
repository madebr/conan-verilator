from conan.packager import ConanMultiPackager
import platform


if __name__ == "__main__":
    builder = ConanMultiPackager()
    build_requires = None
    if platform.system() == "Windows":
        build_requires = {"*": "mingw_installer/1.0@conan/stable"}
    builder.add(settings={"arch_build": "x86",}, build_requires=build_requires)
    builder.add(settings={"arch_build": "x86_64",}, build_requires=build_requires)
    builder.run()
