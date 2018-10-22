find_program(VERILATOR_BIN
    NAMES verilator
    PATHS /usr/bin ENV VERILATOR_ROOT
    PATHS_SUFFIXES bin
)

if(NOT VERILATOR_BIN)
    message(FATAL_ERROR "Cannot find verilator executable")
endif()

message("Executing ${VERILATOR_BIN} -V")
execute_process(COMMAND "${VERILATOR_BIN}" -V
    OUTPUT_VARIABLE VERILATOR_VERBOSE_VERSION
)
message("Executed")
string(REGEX MATCH "[ \t]VERILATOR_ROOT[ \t]+=[ \t]([^\n\r]*)" VER_ROOT_MATCH "${VERILATOR_VERBOSE_VERSION}")
if(NOT VER_ROOT_MATCH)
    message(FATAL_ERROR "Could not determine VERILATOR_ROOT")
endif()
set(VERILATOR_ROOT "${CMAKE_MATCH_1}")
message(STATUS "VERILATOR_ROOT=${VERILATOR_ROOT}")

find_package(Perl REQUIRED)
find_package(Threads REQUIRED)

set(VERILATOR_COVERAGE_BIN "${PERL_EXECUTABLE}" "${VERILATOR_ROOT}/bin/verilator_coverage")  # FIXME: path is incorrect
set(VERILATOR_INCLUDER_BIN "${PERL_EXECUTABLE}" "${VERILATOR_ROOT}/bin/verilator_includer")

set(VERILATOR_CXX_STANDARD gnu++14)
# Compiler flags to use to turn off unused and generated code warnings, such as -Wno-div-by-zero
set(VERILATOR_CXX_NO_UNUSED -faligned-new -Wno-bool-operation -Wno-sign-compare
    -Wno-uninitialized -Wno-unused-but-set-variable -Wno-unused-parameter -Wno-unused-variable -Wno-shadow)
# Compiler flags that turn on extra warnings
set(VERILATOR_CFLAGS_EXTRA -Wextra -Wfloat-conversion -Wlogical-op)


# VM_SC: SystemC mode
# VM_SP_OR_SC: Legacy or SystemC output mode?  0/1 (from --sc)
# SYSTEMC_INCLUDE ?= systemC includedir
# SYSTEMC_LIBDIR ?=  systemc librarydir


#VK_CPPFLAGS_ALWAYS += \
#		-MMD \
#		-I$(VERILATOR_ROOT)/include \
#		-I$(VERILATOR_ROOT)/include/vltstd \
#		-DVL_PRINTF=printf \
#		-DVM_COVERAGE=$(VM_COVERAGE) \
#		-DVM_SC=$(VM_SC) \
#		-DVM_TRACE=$(VM_TRACE) \
#		$(CFG_CXXFLAGS_NO_UNUSED) \