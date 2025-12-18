Recreation Math Library Documentation (v.1.0). 2025, 14Alfa. All rights reserved.

Recreation Math (RecMath) is a strong, complete math library. Its objective is to import all kinds of math functions and objects in a familiar way in Python.
RecMath introduces 30 main functions alongside 4 new classes of objects not found in regular Python (constants, matrices, vectors and quaternions)

------ INDEX ------
1. Initialize the RecMath library
2. New exceptions found in RecMath
3. New Objects implemented in RecMath
    3.1: Constants ('constant' class)
    3.2: Matrices ('matrix' class)
    3.3: Vectors ('vector' class)
    3.4: Quaternions ('quaternion' class)
4. New Functions implemented in RecMath

------------------------------------------------------------------------------------------------------------------------------------------
1. Initialize the RecMath library

The RecMath library initialization follows 2 paths:
    - 'main' approach: importing all modules at once:
        * import RecMath.main as recmath

    - 'alternate' approach: importing individual modules:
        * from RecMath import main as recmath
        * from RecMath import constant as const
        * from RecMath import matrix as mat
        * from RecMath import vector as vct
        * from RecMath import quaternion as qtn

It is important that the RecMath folder is in the SAME directory that you are working on. If this is not the case, then the library will not work.

2. New exceptions found in RecMath

RecMath implements one new exception for dealing with the new functions and objects:
    - InputError: This exception is generated when a variable exceeds its definition limits.
    This is RecMath way of saying 'You f****ed/messed up'

3. New Objects implemented in RecMath

RecMath implements 4 new objects not found in Python:
    - Constants:    Not a proper datatype, but a collection of the most important real life constants.
    - Matrices:     Datatype that implements matrices as lists of lists of real numbers.
    - Vectors:      Datatype that implements vectors as tuples of real numbers.
    - Quaternions:  Datatype that implements quaternions with variables.

3.1: Constants ('constant' class)

This module imports 8 constants and 2 sequences of constants. As we've said before, we consider this not to be a datatype, but a collection of constants.
Internally, the object 'constant' acts as the key to all of these constants, as all of them are considered 'float' numbers.

The imported constants are the following:
    -> Exact Constants: Constants that have a fixed, computable value:
        * const.pi:         It outputs pi = 3.14159...
        * const.euler:      It outputs e = 2.71828...
        * const.tau:        It outputs tau = 2*pi = 6.28318...
        * const.plastic:    It outputs the plastic constant, the only real solution to x^3 = x + 1
        * const.dottie:     It outputs the constant d, the only real solution to cos(d)=d
    
    -> Sequences of Constants: Sequences with important constants in its values:
        * const.mettalic:   It outputs the n-th metallic number, being n an inputted number
        * const.harmonic:   It outputs the n-th harmonic number = sum from 1 to n of 1/k
    
    -> Iterative Methods: Constants which definition involves infinite summations, so the library can only output an approximation.
       We recommend 1.000.000 iterations for precision, 10.000 iterations for speed.
        * const.gamma:      It outputs an aproximation of gamma, with "n" being no. of iterations.
        * const.apery:      It outputs an approximation of zeta(3) = inf sum of 1/n^3, with "it" being the no. of iterations.
        * const.catalan:    It outputs an approximation of G = infinite sum of (-1)^n / (2n+1)^2, with "it" being the no. of iterations.

3.2: Matrices ('matrix' class)

This module imports real matrices as a new datatype, composed of lists of lists of numbers:
(A list of nº of files elements, each element being a list with nº of rows elements ---> M[file][row])
This 'matrix' is stored in the object variable .state

Alongside the definition of matrices, this module imports 13 new operations for dealing with the new matrices:
    * mat.fancy:            It outputs the self.state matrix in a better console display
    * mat.elementSet:       It overwrites the element (i,j) in the matrix self.state
    * mat.zeros:            It creates an empty matrix, with 'files' files and 'rows' rows, and stores it in self.state
    * mat.nths:             It creates a matrix with 'files' files and 'rows' rows, each element being n, and stores it in self.state
    * mat.eye:              It creates the n-th identity matrix / n x m Hermite normal form, and stores it in self.state
    * mat.transpose:        It transposes the self.state matrix and stores it in exit_variable.state
    * mat.triangular:       It creates a triangular matrix based on the self.state matrix and the isUp value (1=UpperTri, 0=LowerTri), stored on exit_variable.state
    * mat.diag:             It creates a square matrix with the inputted list in its main diagonals, and stores it on self.state
    * mat.trace:            It outputs the trace of the self.state matrix.
    * mat.addSubtract:      It outputs the sum/difference between self.state and other.state matrices (depending on the isSum argument).
    * mat.singleOperator:   It outputs the opposite/absolute of the self.state matrix (depending on the isOpp argument)
    * mat.scalarMult:       It outputs the scalar multiplication of the self.state matrix and an inputted scalar
    * mat.matrixMult:       It outputs the matrix product A*B, A and B being self.state and other.state, respectively.

3.3: Vectors ('vector' class)

This module imports real vectors as a new datatype, composed of tuples of real numbers.
This datatype needs a number when a new object is defined: the 'length' argument, which specifies the length of the vector.
This vector is stored in the object variable .state, and is initialized as the zero vector with length 'length'.

Alongside the definition of vectors, this module imports 10 new operations for dealing with the new vectors:
    * vct.vectorSet:        It overwrites the self.state vector in favour of the inputted list.
    * vct.module:           It outputs the module of the vector self.state
    * vct.normalize:        It normalizes the self.state vector (|v|=1), and stores it in exit_variable.state
    * vct.sum:              It outputs self.state + vct.state vector, and stores it in exit_variable.state
    * vct.subtract:         It outputs self.state - vct.state vector, and stores it in exit_variable.state
    * vct.scalarMult:       It outputs k * self.state, and stores it in exit_variable.state
    * vct.dot:              It outputs the dot product between self.state and vct.state
    * vct.angleBetween:     It outputs the angle (in radians unless specified) between self.state and vct.state
    * vct.cross:            It outputs the 3D cross product of self.state and vct.state, and stores it in exit_variable.state
    * vct.mixed:            It outputs the 3D mixed product of self.state, v1.state and v2.state, and stores it in exit_variable.state

3.4: Quaternions ('quaternion' class)

This module imports quaternions as a new datatype, composed of four object variables symbolizing the 4 quaternion coordinates (self.real, self.i, self.j and self.k).

Alongside the definition of quaternions, this module imports 12 new operations for dealing with the new quaternions:
    * qtn.fancy:            It outputs the quaternion self in a better console display.
    * qtn.norm:             It outputs the module/norm of the quaternion self.
    * qtn.normalize:        It normalizes the self quaternion (||q||=1), and stores it in exit_variable.
    * qtn.conj:             It outputs the conjugate of self, and stores it in exit_variable.
    * qtn.sum:              It outputs the sum of self and q2, and stores it in exit_variable.
    * qtn.subtract:         It outputs self - q2, and stores it in exit_variable.
    * qtn.scalarMult:       It outputs the scalar product between n and self, and stores it in exit_variable.
    * qtn.product:          It outputs self * q2 (IN THAT ORDER!!), and stores it in exit_variable. We use the scalar-vector multiplication for this method.
    * qtn.inverse:          It outputs the inverse of the quaternion self, and stores it in exit_variable.
    * qtn.division:         It outputs the division between self and q2, and stores it in exit_variable. The executed operation depends on the isLeft argument.
    * qtn.exp:              It outputs exp(self), and stores it in exit_variable.
    * qtn.quaternicLog:     It outputs ln(self), and stores it in exit_variable.

4. New Functions implemented in RecMath

RecMath implements 31 other functions alongside the new objects. For better display, we have divided the functions in groups.
Note: When dealing with calculus functions, remember that 'func' objects are meant to be lambda functions.

- Divisibility Functions: Functions involving divisibility rules and divisors.
    * recmath.divisors:         It outputs the divisors of a given number, in list form or added.
    * recmath.divisorCount:     It outputs the number of divisors between the inputs a and b, as well as the divisors themselves.
    * recmath.abundanceIndex:   It outputs the abundance index of a number (sum of all divisors over the number itself).
    * recmath.divisorClass:     It outputs whether a number is deficient, perfect or abundant.
    * recmath.areFriends:       It outputs whether 2 inputted numbers are friends i.e., divisors of a == b and divisors of b == a.

- Primality Functions: Functions involving prime numbers.
    * recmath.isPrime:          It outputs whether a number is prime or not.
    * recmath.primesBetween:    It outputs a list containing the prime numbers between the inputs a and b, both included.
    * recmath.areTwinPrimes:    It outputs whether 2 numbers are twin primes, i.e., both numbers are prime and the difference between them is 2.
    * recmath.piFunction:       It outputs the number of primes less than or equal to the inputted number.
    * recmath.primeFact:        It outputs a list containing the prime factorization of an inputted number.

- 'is' Functions: Functions which check a certain condition/property of a number.
    * recmath.isTriangular:     It outputs whether a number is a triangular number or not.
    * recmath.isHexagonal:      It outputs whether a number is a hexagonal number or not.
    * recmath.isNarcissist:     It outputs whether a number is narcissist or not (if the sum of its digits to the length power is equal to itself).
    * recmath.isHarshad:        It outputs whether a number is a Harshad/Niven number or not (if it is divisible by the sum of its digits).
    * recmath.isMunchausen:     It outputs whether a number is a Munchausen number or not (if it is equal to the sum of its digits raised to the power of themselves).
                            
- Proper Math Functions: Functions which have certain uses in mathematics.
    * recmath.nthRoot:          It outputs the n-th root of a given number. We use exponential-logarithm form, so floating point precision can be limited.
    * recmath.sign:             It outputs the sign of a given number (+1 if positive, -1 if negative, 0 if 0).
    * recmath.deltaDirac:       It outputs delta(n), being n the inputted number (delta is infinity if x=0, and 0 if it is NOT 0).
    * recmath.deltaKronecker:   It outputs 1 if both numbers are equal, and 0 elsewhere.
    * recmath.heaviside:        It outputs 1 if x is positive, 1/2 if x is 0, and 0 if x is negative.
    * recmath.ramp:             It outputs x if x is positive, 0 elsewhere.
    * recmath.longDivision:     It outputs the quotient and remainder of the operation a/b.
    * recmath.subFactorial:     It outputs the subfactorial of an inputted number (!n).
    * recmath.primordial:       It outputs the primordial of an inputted number (n#), i.e., the product of all primes less than n.
    * recmath.decimalPart:      It outputs the decimal part of a given number.
    * recmath.linSpace:         It outputs a list containing n elements equally spaced between a and b.
    * recmath.convolve:         It outputs the discrete convolution of the lists/tuples a and b (a*b).
    
- Calculus Functions: Functions which are involved in calculus:
    * recmath.derive:           It outputs the numerical n-th derivative of 'f' in the point 'a' with precision 'h'.
    * recmath.integral:         It outputs the numerical integral of 'f' in the interval [a,b].
    * recmath.fourierSeries:    It outputs the Fourier coefficients of a function 'f' in the interval [a,b] with 'n' iterations.
    * recmath.solveF:           It outputs the solution of f==0 using the Newton-Raphson Method.
