import weakref
import numpy as np
from typing import Callable, Any
from dataclasses import dataclass
from contextlib import contextmanager

class Config:
    enable_backdrop = True

@contextmanager
def config_test():
    #write a preprocess before yield and write a post process in final block
    print("start")
    try:
        yield
    finally:
        print("done")

with config_test():
    print("process")


@contextmanager
def using_config(name,value):
    old_value=getattr(COnfig,name)
    setattr(Config,name,value)
    try:
        yield
    finally:
        setattr(Config,name,old_value)
    




def as_array(x):
    if np.isscalar(x):
        return np.array(x)
    return x


@dataclass
class Variable:
    data: Any
    grad: Any = None
    creator: Callable = None
    generation: int = 0

    def set_creator(self, func):
        self.creator = func
        self.generation = self.generation+1

    def backward(self, retain_grad=False):
        if self.grad is None:
            self.grad = np.ones_like(self.data)
        funcs = []
        seen_set = set()

        def add_func(f):
            if f not in seen_set:
                funcs.append(f)
                seen_set.add(f)
                funcs.sort(key=lambda x: x.generation)
        add_func(self.creator)

        while funcs:
            f = funcs.pop()
            gys = [output().grad for output in f.outputs]
            gxs = f.backward(*gys)
            if not isinstance(gxs, tuple):
                gxs = (gxs,)
            for x, gx in zip(f.inputs, gxs):
                if x.grad is None:
                    x.grad = gx
                else:
                    x.grad = x.grad+gx
                if x.creator is not None:
                    add_func(x.creator)
            if not retain_grad:
                for y in f.ouputs:
                    y().grad = None

    def __post_init__(self):
        if self.data is not None:
            if not isinstance(self.data, np.ndarray):
                raise TypeError(f"{self.data} is not supported")


class Function:
    def __call__(self, *inputs):
        xs = [x.data for x in inputs]
        ys = self.forward(*xs)
        if not isinstance(ys, tuple):
            ys = (ys,)
        outputs = [Variable(as_array(y)) for y in ys]
        # without backdrop ,some variables are needless for reducing memory comsumption
        if Config.enable_backdrop:
            self.generation = max([x.generation for x in inputs]
                                  )
            for output in ouputs:
                output.set_creator(self)
            self.inputs = inputs
            self.outputs = [weakref.ref(output) for output in outputs]
        return outputs if len(outputs) > 1 else outputs[0]

    def forward(self, x):
        NotImplementedError()

    def backwward(self, gy):
        raise NotImplementedError()


def exp(x):
    f = Exp()
    return f(x)


class Add(Function):
    def forward(self, xs):
        x0, x1 = xs
        y = x0+x1
        return y

    def backward(self, gy):
        return gy, gy


def add(x0, x1):
    return Add()(x0, x1)


if __name__ == "__main__":
    x0 = Variable(np.array(1.0))
    x1 = Variable(np.array(1.0))
    t = add(x0, x1)
    y = add(x0, t)
    y.backward()
    print(y.grad, t.grad)
    print(x0.grad, x1.grad)
