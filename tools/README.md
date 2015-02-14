# ################################
# KLEE Build
# ################################

# step0 Download Source: 
git clone https://github.com/klee/klee.git

# step1 Configuration (inside klee source)

./configure --with-llvm=/home/kuan/llvm-2.9 --with-stp=/home/kuan/stp_install --with-uclibc=/home/qirong/Frog/frog_test/tools/klee-uclibc --enable-posix-runtime

# step2 Make (inside klee source)
make ENABLE_OPTIMIZED=1

# ################################
# KLEE Use 
# ################################

# call KLEE:
tools/KLEE_SOURCE_2015_klee/Release+Asserts/bin/klee

# include klee.h:
tools/KLEE_SOURCE_2015/klee/include/klee


