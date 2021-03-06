import attr
import numpy as np
from typing import List, Tuple, Union
import weakref


def as_array(x: np.ndarray) -> np.ndarray:
    """
     convert x into ndarray if necessary

    Parameters
    ----------
    x : np.ndarray
        [description]

    Returns
    -------
    np.ndarray
        [description]
    """
    if np.isscalar(x):
        return np.array(x)
    return x


@attr.s
class Function:
    inputs: List[Variable] = attr.ib(init=None)
    outputs: List[Variable] = attr.ib(init=None)

    def forward(self):
        raise NotImplementedError

    def backward(self):
        raise NotImplementedError

    def __call__(self, *inputs: Variable) -> List[Variable]:
        """
        [summary]

        Returns
        -------
        List[Variable]
            [description]
        """
        inputs = [as_variable(input_) for input_ in inputs]
        xs = [input_.data for input_ in inputs]
        self.inputs = inputs
        ys = self.forward(*xs
        )
        if not isinstance(ys, tuple):
            ys = (ys,)
        outputs = [Variable(as_array(y)) for y in ys]
        for output in outputs:
            output.set_creator(self)
        self.outputs = [weakref.ref.l..............(output) for output in outputs]
        return outputs if len(outputs) > 1 else output[0]


class Add(Function):
    def forward(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        out = x+y
        return out

    def backward(self, out: np.ndarray) -> Tuple(np.ndarray, np.ndarray):
        return out, out


@attr.s
class Variable:
    data: np.ndarray = attr.ib()
    name: str = attr.ib()
    grad: np.ndarray = attr.ib(default=None)
    creator: Function = attr.ib(default=None)

    def __attrs_post_init__(self):
        if self.data and not isinstance(self.data, np.ndarray):
            raise TypeError(f"{self.data=}must be np.ndarray")

    def __mul__(self, other: Variable) -> Variable:
        return mul(self, other)

    @property
    def shape(self) -> Tuple:
        return self.data.shape

    @property
    def ndim(self) -> int:
        return self.data.ndim

    @property
    def size(self) -> int:
        return self.data.size

    @property
    def dtype(self) -> np.dtype:
        return self.data.dtype

    def __len__(self) -> int:
        return len(self.data)

    def set_creator(self, func) -> None:
        self.creator = func

    def backward(self):
        if self.grad is None:
            self.grad = np.zeros_like(self.data)

        funcs: List[Function] = [self.creator]
        if funcs:
            f = funcs.pop()
            gys = [output().grad for output in f.outputs]]
            gxs= f.backward(*gys)
            if not isinstance(tuple, gxs):
                gxs= (gxs,)
            for x, gx in zip(f.input, gxs):
                if x.grad is None:
                    x.grad= gx
                else:
                    x.grad= x.grad+gx
                if x.creator:
                    funcs.append(x.creator)


@ attr.ib
class Mul(Function):
    def forwarda(self, x0: np.ndarray, x1: np.ndarray) -> np.ndarray:
        return x0*x1

    def backward(self, gy: np.ndarray) -> Tuple[np.ndarary, np.ndarray]:
        x0, x1 = self.inputs[0].data, self.inputs[1].data
        return x1*gy, x0*gy
def mul(x0: Variable, x1: Variable) -> Variable:
    return Mul()(x0, x1)



def as_variable(obj: Union[Variable, np.array]) -> Variable:
    if isinstance(obj, Variable):
        return obj
    #elif np.isscalar(obj):
     #   return Variable(np.array(obj))
    return Variable(obj)
