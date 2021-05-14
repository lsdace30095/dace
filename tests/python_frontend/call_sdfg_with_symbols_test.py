# Copyright 2019-2021 ETH Zurich and the DaCe authors. All rights reserved.
import numpy as np
import dace

N = dace.symbol("N")

@dace.program
def add_one(A: dace.int64[N, N], result: dace.int64[N, N]):
    result[:] = A + 1


def call_test():
    @dace.program
    def add_one_more(A: dace.int64[N, N]):
        result = dace.define_local([N, N], dace.int64)
        add_one(A, result)
        return result + 1

    A = np.random.randint(0, 10, size=(11, 11), dtype=np.int64)
    result = add_one_more(A=A.copy())
    assert np.allclose(result, A + 2)


def call_sdfg_test():
    add_one_sdfg = add_one.to_sdfg()

    @dace.program
    def add_one_more(A: dace.int64[N, N]):
        result = dace.define_local([N, N], dace.int64)
        add_one_sdfg(A=A, result=result)
        return result + 1

    A = np.random.randint(0, 10, size=(11, 11), dtype=np.int64)
    result = add_one_more(A=A.copy())
    assert np.allclose(result, A + 2)


def call_sdfg_argnames_test():
    add_one_sdfg = add_one.to_sdfg()

    @dace.program
    def add_one_more(A: dace.int64[N, N]):
        result = dace.define_local([N, N], dace.int64)
        add_one_sdfg(A, result=result)
        return result + 1

    A = np.random.randint(0, 10, size=(11, 11), dtype=np.int64)
    result = add_one_more(A=A.copy())
    assert np.allclose(result, A + 2)


S1 = dace.symbol("S1")
S2 = dace.symbol("S2")

sdfg = dace.SDFG('internal')
sdfg.add_array('inp', shape=[N, N], dtype=dace.float32, strides=[S1, S2])
state = sdfg.add_state()
t = state.add_tasklet('p', {'i'}, set(), 'printf("hello world %f\\n", i)')
r = state.add_read('inp')
state.add_edge(r, None, t, 'i', dace.Memlet.simple('inp', 'N-1, N-1'))

@dace.program
def caller(A: dace.float32[N, N]):
    sdfg(inp=A)


def call_sdfg_with_stride_symbols():
    A = np.random.rand(4,4).astype(np.float32)
    caller(A)
    print('Should print', A[-1,-1])



other_N = dace.symbol("N")


@dace.program
def add_one_other_n(A: dace.int64[other_N - 1, other_N - 1],
                    result: dace.int64[other_N - 1, other_N - 1]):
    result[:] = A + 1


def call_sdfg_same_symbol_name_test():
    add_one_sdfg = add_one_other_n.to_sdfg()

    @dace.program
    def add_one_more(A: dace.int64[N, N]):
        result = dace.define_local([N, N], dace.int64)
        add_one_sdfg(A=A, result=result)
        return result + 1

    A = np.random.randint(0, 10, size=(11, 11), dtype=np.int64)
    result = add_one_more(A=A.copy())
    assert np.allclose(result, A + 2)


if __name__ == "__main__":
    call_test()
    call_sdfg_test()
    call_sdfg_argnames_test()
    call_sdfg_with_stride_symbols()
    call_sdfg_same_symbol_name_test()
