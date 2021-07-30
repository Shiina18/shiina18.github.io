---
title: "Hands-on experience with a constrained least squares problem"
categories: Tech
updated: 2021-07-28
comments: true
mathjax: true
---

主问题是个特别简单的凸优化问题, 找包调的时候顺便看了看 SciPy 处理一般带约束优化问题的不同算法的适用场景 (官方文档里并没有写得很明白). 主要讲调包, 没有数学.

Consider the following quadratic programming (QP) problem, 

$$
\begin{align*}
\min_\beta  & \quad \Vert Y - X\beta \Vert_2^2, \\
\text{subject to} & \quad \boldsymbol{1}_p'\beta = 1, \\
& \quad \beta \succeq 0,
\end{align*}
$$

with

- an $n \times 1$ vector $Y$,
- an $n \times p$ matrix $X$, and
- a $p \times 1$ vector  $\beta$.

<!-- more -->

The notation $\boldsymbol{1}_p$ stands for the $p\times 1$ vector $(1, \dots, 1)'$. The objection is equivalent to minimizing $\beta' X'X \beta - 2Y'X\beta$. 

Here are two candidate solutions currently, a SciPy solution and a CVXOPT solution.

Side note: The vector $\beta$ can be viewed as a probability distribution over $p$ column vectors of $X$, and thus $X\beta$ is simply the expectation of the underlying random vector. This fact is not leveraged in the following post.

## The SciPy solution

SciPy implements three methods to solve **general constrained minimization problems**: trust-region constrained algorithm (trust-constr), sequential least squares programming (SLSQP) algorithm and constrained optimization by linear approximation (COBYLA) algorithm; see [here](https://docs.scipy.org/doc/scipy/reference/tutorial/optimize.html#constrained-minimization-of-multivariate-scalar-functions-minimize) for the problem formulation, and [here](https://docs.scipy.org/doc/scipy/reference/reference/generated/scipy.optimize.minimize.html#scipy.optimize.minimize) for the documentation of the `minimize` function.

### Which to use?

**Use COBYLA if there are non-smooth functions**

COBYLA is an non-gradient based method based on linear approximations to the objective function and each constraint. The algorithm operates by evaluating the objective function and the constrains at the vertices of a trust region. See [here](https://cossan.co.uk/wiki/index.php/COBYLA) for a brief introduction for COBYLA and [here](https://optimization.mccormick.northwestern.edu/index.php/Trust-region_methods) for trust region methods..

> In general, the convergence of COBYLA is slower than that of gradient-based algorithms, i.e. more function evaluations are required to find the optimum. However, one of the salient features of COBYLA is its stability and the low number of parameters to be tuned for performing optimization.

**Use SLSQP for moderately large problems**

Kraft (1988) claims that sequential quadratic programming is known as to be *the most efficient* computation method to solve the general nonlinear programming problem with **continuously differentiable** objective function and constraints. 

The size of the problem should only be **moderately large** with $m \le p \le 200$, where $m$ (=1 in our case) is the number of equality and inequality constraints (with bounds excluded), and $p$ is the dimension of the variable to be optimized. Wendorff et al. (2016) reported in their case study that SLSQP is not able to be run in parallel making a problem with large number of design variables intractable.

**Use trust-constr method for large-scale problems**

> It is the most versatile constrained minimization algorithm implemented in SciPy and the most appropriate for large-scale problems. 

For equality constrained problems it is an implementation of Byrd-Omojokun Trust-Region SQP method. When inequality constraints are imposed as well, it swiches to the trust-region interior point method described in *An interior point algorithm for large-scale nonlinear programming* (Byrd et al., 1999).

Byrd et al. (1999) assume in the paper that first and second derivatives of the objective function and constraints are available, but their strategy can be extended to make use of quasi-Newton approximations. Their algorithm incorporates within the interior point method two powerful tools for solving nonlinear problems: sequential quadratic programming (SQP) and trust region techniques.

**References**

- Kraft, D. (1988). [A software package for sequential quadratic programming](http://degenerateconic.com/wp-content/uploads/2018/03/DFVLR_FB_88_28.pdf). *Tech. Rep. DFVLR-FB* 88-28, DLR German Aerospace Center – Institute for Flight Mechanics, Koln, Germany.
- Wendorff, A., Botero, E., & Alonso, J. J. (2016). [Comparing Different Off-the-Shelf Optimizers' Performance in Conceptual Aircraft Design](http://adl.stanford.edu/papers/botero_wendorff.pdf). In *17th AIAA/ISSMO Multidisciplinary Analysis and Optimization Conference* (p. 3362).
- Byrd, R. H., Hribar, M. E., & Nocedal, J. (1999). An interior point algorithm for large-scale nonlinear programming. *SIAM Journal on Optimization*, *9*(4), 877-900.

## The CVXOPT solution

Though lesser-known, it is a dedicated package for convex optimization, and **can solve a more tailored problem suitable for our case**.

### Usage

See [here](https://cvxopt.org/userguide/coneprog.html#quadratic-programming) for the description of the function to solve QPs. Below is the notation mapping table, where $I_p$ is the $p \times p$ identity matrix.

| cvxopt |            original |
| -----: | ------------------: |
|    $x$ |             $\beta$ |
|    $P$ |              $2X'X$ |
|    $q$ |             $-2X'Y$ |
|    $G$ |              $-I_p$ |
|    $h$ |  $\boldsymbol{0}_p$ |
|    $A$ | $\boldsymbol{1}_p'$ |
|    $b$ |                   1 |

**Outputs**

The function `cvxopt.solvers.qp` returns a dictionary with keys for some properties about the solution among which the 'status', 'x', and 'primal objective' are probably the most important. Read the docstring for more detail.

The 'status' field has values 'optimal' or 'unknown'. 

- If the status is 'optimal', 'x' is an approximate solution of the primal optimal solutions, and 'primal objective' is the value of the primal objective.
- If the status is 'unknown', 'x' is the last iterate before termination. 

### Technical notes

There is a report [The CVXOPT linear and quadratic cone program solvers](http://www.ee.ucla.edu/~vandenbe/publications/coneprog.pdf) (pdf) listed in its [technical documentation](https://cvxopt.org/documentation/index.html#technical-documentation). According to p. 11 of the report, QPs are solved using a path-following algorithm which is a kind of interior-point algorithms.

## Test

Based on the discussion above, SLSQP is used for SciPy.

```python
import time

import cvxopt
import numpy as np
import tqdm
from scipy import optimize


def random_matrix(size):
    return cvxopt.matrix(np.random.random_sample(size))


# used in scipy
def objection(beta, X, Y):
    """
    Parameters
    ----------
    beta : array (p,)
    X : array (n, p)
    Y : array (n,)

    Returns
    -------
    scalar
    """
    bias = Y - X.dot(beta)
    return bias.dot(bias)


def jac(beta, X, Y):
    """
    Parameters
    ----------
    beta : array (p,)
    X : array (n, p)
    Y : array (n,)

    Returns
    -------
    array (p,)
    """
    return 2 * (X.T.dot(X).dot(beta) - X.T.dot(Y))
```

Run the test

```python
np.random.seed(0xC7)
cvxopt.solvers.options['show_progress'] = False
count = 0
time_cvx = 0
time_sci = 0
count_cvx_fail = 0
count_sci_fail = 0
loss_relative_diff = 0

times = 100
for _ in tqdm.tqdm(range(times)):
    # cvxopt
    X = random_matrix((1000, 100))
    n, p = X.size  # should be X.shape if X is an numpy array
    Y = random_matrix((n, 1))

    # cvxopt notation
    P = 2 * X.T * X  # * means matrix multiplication in CVXOPT
    q = -2 * X.T * Y
    G = - cvxopt.matrix(np.eye(p))
    h = cvxopt.matrix(0.0, size=(p, 1))
    A = cvxopt.matrix(1.0, size=(1, p))
    b = cvxopt.matrix(1.0)

    start_time = time.time()
    res_cvx = cvxopt.solvers.qp(P, q, G, h, A, b)
    time_cvx += time.time() - start_time

    if res_cvx['status'] != 'optimal':
        count_cvx_fail += 1
        print('CVXOPT failed')
    loss_cvx = res_cvx['primal objective'] + (Y.T * Y)[0]

    # scipy
    X = np.array(X)
    Y = np.array(Y).ravel()  # shape (n,)

    eq_cons = {'type': 'eq',
               'fun': lambda beta: np.ones(beta.shape[0]).dot(beta) - 1,
               'jac': lambda beta: np.ones(beta.shape[0])}

    start_time = time.time()
    res_sci = optimize.minimize(objection,
                                x0=(1 / p) * np.ones(p),
                                args=(X, Y),
                                method='SLSQP',
                                jac=jac,
                                bounds=optimize.Bounds(lb=0, ub=np.inf),
                                constraints=eq_cons)
    time_sci += time.time() - start_time

    if not res_sci['success']:
        count_sci_fail += 1
        print('SciPy failed')
    loss_sci = res_sci['fun']

    is_cvx_better = loss_cvx <= loss_sci
    # print(is_cvx_better, loss_cvx, loss_sci)
    loss_relative_diff += (loss_cvx - loss_sci) / loss_sci
    count += is_cvx_better

print(f'In a test that randomly generates {n} x {p} matrix X and other vectors for {times} times')
print(f'CVXOPT achieved a better solution {count}/{times} times')
print(f'CVXOPT averagely achieved {100 * loss_relative_diff / times:.8f}% higher loss')
print(f'cvxopt.solvers.qp cost {time_cvx:.2f}s, failed {count_cvx_fail} times')
print(f'scipy.optimize.minimize cost {time_sci:.2f}s, failed {count_sci_fail} times')
```

### Results

**Note that we only used SLSQP method in SciPy**, while `trust-constr` is said to be the most appropriate for large-scale problems.

It seems that 

- CVXOPT tends to achieve negligibly higher loss.
- CVXOPT runs significantly faster even when dealing with large matrices.
- SLSQP does fail to converge with default parameters when dealing with large matrices. 

```
In a test that randomly generates 1000 x 100 matrices Xs and other vectors for 100 times
CVXOPT achieved a better solution 0/100 times
CVXOPT averagely achieved 0.00002240% higher loss
cvxopt.solvers.qp cost 1.06s, failed 0 times
scipy.optimize.minimize cost 25.03s, failed 0 times
```

```
 60%|██████    | 18/30 [01:29<00:57,  4.76s/it]SciPy failed
In a test that randomly generates 1000 x 300 matrices Xs and other vectors for 30 times
CVXOPT achieved a better solution 2/30 times
CVXOPT averagely achieved 0.00002022% higher loss
cvxopt.solvers.qp cost 1.02s, failed 0 times
scipy.optimize.minimize cost 145.52s, failed 1 times
```

```
In a test that randomly generates 22 x 5 matrices Xs and other vectors for 5000 times
CVXOPT achieved a better solution 1616/5000 times
CVXOPT averagely achieved 0.00001793% higher loss
cvxopt.solvers.qp cost 9.48s, failed 0 times
scipy.optimize.minimize cost 5.80s, failed 0 times
```

```
In a test that randomly generates 10000 x 1000 matrix X and other vectors for 5 times
CVXOPT achieved a better solution 5/5 times
CVXOPT averagely achieved -0.02020533% higher loss
cvxopt.solvers.qp cost 3.13s, failed 0 times
scipy.optimize.minimize cost 1316.03s, failed 5 times
```