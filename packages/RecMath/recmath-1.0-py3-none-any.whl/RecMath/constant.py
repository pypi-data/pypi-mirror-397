"""
Constant Module of the library RecMath. It imports the 'constant' class 
(collection of the most important real life constants).
"""
import math

class InputError(Exception):
    def __init__(self, *args):
        """This is RecMath's way of saying: you f***ed/messed up"""
        super().__init__(*args)

# "constant"  class:
class constant(float):
    """
    Constant class. This datatype is a subclass of the 'float' datatype, and it can be characterized as
    not a datatype, but a collection of the most important real life constants.
    """
    def __init__(self):
        """
        Constant class. This datatype is a subclass of the 'float' datatype, and it can be characterized as
        not a datatype, but a collection of the most important real life constants.
        """
        super().__init__()

    # ------------- Exact Constants -------------
    # Ex.1: Pi Method. It outputs pi = 3.14159...
    def pi(self) -> float:
        """It outputs pi = 3.14159..."""
        return math.pi()
    
    # Ex.2: e Method. It outputs e = 2.71828...
    def euler(self) -> float:
        """It outputs e = 2.71828..."""
        return math.e()

    # Ex.3: Tau Method. It outputs tau = 2*pi = 6.28318...
    def tau(self) -> float:
        """It outputs tau = 2*pi = 6.28318..."""
        return math.tau()
    
    # Ex.4: Plastic Number/Ratio Method. It outputs the plastic constant, the only real solution to x^3 = x + 1.
    def plastic(self) -> float:
        """It outputs the plastic constant, the only real solution to x^3 = x + 1"""
        sum1=math.cbrt((9+math.sqrt(69))/18)
        sum2=math.cbrt((9-math.sqrt(69))/18)
        return sum1+sum2
    
    # Ex.5: Dottie Number Method. It outputs the constant d, the only real solution to cos(d)=d
    def dottie(self) -> float:
        """It outputs the constant d, the only real solution to cos(d)=d"""
        d=1
        while d!=math.cos(d):
            d=math.cos(d)

        return d
    
    # ------------- Sequences of Constants -------------
    # SC.1: Metallic Constants Method. It outputs the n-th metallic number, being n an inputted number.
    def metallic(self,n:int) -> float:
        """It outputs the n-th metallic number, being n an inputted number."""
        if n!=math.floor(n) or n<0: # The number must be an integer greater than 0:
            raise InputError("The input number 'n' must be an integer and greater than 0")

        return (n+math.sqrt((n**2)+4))/2

    # SC.2: Harmonic Numbers Method. It outputs the n-th harmonic number = sum from 1 to n of 1/k
    def harmonic(self,n:int) -> float:
        """It outputs the n-th harmonic number = sum from 1 to n of 1/k"""
        if n!=math.floor(n) or n<0: # The number must be an integer greater than 0:
            raise InputError("The input number 'n' must be an integer and greater than 0")

        result=0
        for i in range(1,n+1):
            result+=1/i

        return result

    # ------------- Iterative Methods ------------- 
    # It.1: Euler-Mascheroni Constant Method. It outputs an aproximation of gamma, with "n" being no. of iterations. We reccomend:
    # Precision -> ~1.000.000 iterations (5 correct decimal places)
    # Speed     -> ~10.000 iterations (4 correct decimal places)
    def gamma(self,n:int) -> float:
        """
        It outputs an aproximation of the Euler-Mascheroni constant gamma, with "n" being number of iterations. We reccomend:
        - Precision -> ~1.000.000 iterations (5 correct decimal places)
        - Speed     -> ~10.000 iterations (4 correct decimal places)
        """
        summation=constant().harmonic(n)
        return summation-math.log(n)

    # It.2: Apéry's Constant Method. It outputs an approximation of zeta(3) = inf sum of 1/n^3, with "it" being the no. of iterations.
    # We reccomend:
    # Precision -> ~1.000.000 iterations (11 correct decimal places)
    # Speed     -> ~10.000 iterations (6 correct decimal places)
    def apery(self,it:int) -> float:
        """
        It outputs an approximation of zeta(3) = inf sum of 1/n^3, with "it" being the no. of iterations. We reccomend:
        - Precision -> ~1.000.000 iterations (11 correct decimal places)
        - Speed     -> ~10.000 iterations (6 correct decimal places)
        """
        if it!=math.floor(it) or it<0: # The number must be an integer greater than 0:
            raise InputError("The number of iterations must be an integer and greater than 0")

        result=0
        for n in range(1,it+1):
            result+=(1/(n**3))

        return result
    
    # It.3: Catalan's Constant Method. It outputs an approximation of G = infinite sum of (-1)^n / (2n+1)^2
    # We reccomend:
    # Precision -> ~1.000.000 iterations (12 correct decimal places)
    # Speed     -> ~10.000 iterations (9 correct decimal places)
    def catalan(self,n:int) -> float:
        """
        It outputs an approximation of G = infinite sum of (-1)^n / (2n+1)^2. We reccomend:
        - Precision -> ~1.000.000 iterations (12 correct decimal places)
        - Speed     -> ~10.000 iterations (9 correct decimal places)
        """
        result=0
        for i in range(n+1):
            result+=((-1)**i)/((2*i+1)**2)

        return result