# RecMath Library (v.1.0.). A strong, complete math library.
"""RecMath Library. A strong, complete math library."""
# Libraries needed to run RecMath: math
import math

# New exceptions implemented in RecMath: InputError
class InputError(Exception):
    def __init__(self, *args):
        """This is RecMath's way of saying: you f***ed/messed up"""
        super().__init__(*args)


# New objects implemented in RecMath:
# "constant"  class:
from RecMath import constant

# "matrix"  class:
# Note: These matrices are bulit using Python Lists -> A matrix is defined as:
# -> A list of nº of files elements, each element being a list with nº of rows elements ---> M[file][row]
# m=matrix() defines an object matrix. With m.zeros(files,rows), you create a matrix stored in m.state
from RecMath import matrix

# "vector" class:
# Initializing vectors -> v=vector(length='number') -> With this command, a vector of 'number' elements is stored as a tuple in self.state
from RecMath import vector

# "quaternion" class:
from RecMath import quaternion

# ------------------------------------------ Functions implemented in RecMath ---------------------------------------------------
# ------------- Access Functions -------------
# Ac.1: Integer Check Function. It checks if the given variable is a positive integer, otherwise raise exception.
def intCheck(n:int) -> None:
    """It checks if the given variable is a positive integer, otherwise raise exception."""
    if n!=math.floor(n) or n<0: # The number must be an integer greater than 0:
        raise InputError(f"The input number must be an integer and greater than 0")
    
# ------------- Divisibility Functions -------------
# Div.1: Divisors Function. It outputs the divisors of a given number, in list form or added.
def divisors(n:int,proper:bool=None,add:bool=None) -> (int | list):
    """It outputs the divisors of a given number, in list form or added depending on the 'add' parameter."""

    intCheck(n) # Check if n is positive integer

    if proper!=None and proper==True: # We want the PROPER DIVISORS -> range(1,a)
        fin=n
    else: # We want all the divisors -> range(1,a+1)
        fin=n+1

    div_list=[]
    # Calculate the divisors:
    for i in range(1,fin):
        if n%i==0:
            # i is a divisor of a:
            div_list.append(i)

    if add!=None and add==True: # We want the SUM of the divisors:
        return sum(div_list)

    return div_list

# Div.2: divisorCount Function. It outputs the number of divisors between the inputs a and b, as well as the divisors themselves.
def divisorCount(n:int,a:int,b:int,wantDivList:bool=None) -> (tuple[list, int] | int):
    """It outputs the number of divisors between the inputs a and b, as well as the divisors themselves,
    depending on the 'wantDivList' parameter"""

    if a<0 or b>n: # The interval falls out of bounds:
        raise InputError("The limit numbers must be in the range [0,n]")
    
    div=divisors(n)
    betweenDivs=[]

    for i in div:
        if i>=a and i<=b: # The divisor falls in the range
            betweenDivs.append(i)

    if wantDivList!=None and wantDivList==True: # We want the list containing the divisors, as well as its length:
        return betweenDivs, len(betweenDivs)
    else: # We only want the length:
        return len(betweenDivs)

# Div.3. abundanceIndex function. It outputs the abundance index of a number (sum of all divisors over the number itself)
def abundanceIndex(n:int) -> float:
    """It outputs the abundance index of a number (sum of all divisors over the number itself)."""
    div=divisors(n,False,True)
    return div/n

# Div.4: divisorClass function: It outputs whether a number is deficient, perfect or abundant.
# Deficient:    sum(properDivisors) < number -> The function outputs -1
# Perfect:      sum(properDivisors) = number -> The function outputs 0
# Abundant:     sum(properDivisors) > number -> The function outputs 1
def divisorClass(n:int,screen:bool=None) -> int:
    """
    It outputs whether a number is deficient, perfect or abundant.
    - Deficient:    sum(properDivisors) < number -> The function outputs -1
    - Perfect:      sum(properDivisors) = number -> The function outputs 0
    - Abundant:     sum(properDivisors) > number -> The function outputs 1

    The 'screen' parameter indicates if the data must be printed in console or not.
    """
    intCheck(n) # Check if n is positive integer

    # Calculate the sum of its divisors, without the number itself -> Sum of proper divisors
    div_n=divisors(n,True,True)

    if screen!=None and screen==True:
        if div_n>n: # The number is Abundant
            print(f"The number is Abundant: {div_n} > {n}")
        elif div_n<n: # The number is Deficient
            print(f"The number is Deficient: {div_n} < {n}")
        else: # The number is Perfect
            print(f"The number is Perfect: {div_n} = {n}")
    
    # Check the conditions:
    if div_n>n: # The number is Abundant
        return 1
    elif div_n<n: # The number is Deficient
        return -1
    else: # The number is Perfect
        return 0

# Div.5: areFriends Function. It outputs whether 2 inputted numbers are friends i.e., sigma(a)==b and sigma(b)==a.
def areFriends(a:int,b:int) -> bool:
    """It outputs whether 2 inputted numbers are friends i.e., divisors of a == b and divisors of b == a."""
    intCheck(a) # Check if a is positive integer
    intCheck(b) # Check if b is positive integer
    
    # We calculate the sum of divisors of a and b, EXCLUDING a and b -> Sum of proper divisors of a and b
    div_a=divisors(a,True,True)
    div_b=divisors(b,True,True)

    # Check the condition:
    if div_a==b and div_b==a:
        return True
    
    return False


# ------------- Primality Functions -------------
# Prime.1: isPrime Function. It outputs whether a number is prime or not.
def isPrime(n:int) -> bool:
    """It outputs whether a number is prime or not."""
    intCheck(n) # Check if n is positive integer

    fact=divisors(n)
    if len(fact)==2: # The number is prime
        return True
    
    # Else, the number is NOT prime
    return False

# Prime.2: primesBetween Function. It outputs a list containing the prime numbers between the inputs a and b.
def primesBetween(a:int,b:int) -> list:
    """It outputs a list containing the prime numbers between the inputs a and b, both included."""
    primeList=[]

    for i in range(a,b+1):
        if isPrime(i)==True:
            primeList.append(i)

    return primeList

# Prime.3: areTwinPrimes function. It outputs whether 2 numbers are twin primes: both prime, diff==2.
def areTwinPrimes(a:int,b:int) -> bool:
    """It outputs whether 2 numbers are twin primes, i.e., both numbers are prime and the difference between them is 2."""

    intCheck(a) # Check if a is positive integer
    intCheck(b) # Check if b is positive integer

    # Check primality of both numbers:
    prime_a=isPrime(a)
    prime_b=isPrime(b)
    # If the numbers are NOT prime, then the function returns false:
    if prime_a==False or prime_b==False:
        return False
    
    # If the function is STILL going -> Both numbers are prime -> Check if twin prime:
    if abs(a-b)==2: # Twin Primes
        return True
    else: # Both Primes, though not twin
        return False

# Prime.4: Prime Counter Function. It outputs the number of primes less than or equal to the inputted number.
def piFunction(n:int) -> int:
    """It outputs the number of primes less than or equal to the inputted number."""
    intCheck(n) # Check if n is positive integer
    
    primeList=primesBetween(1,n)

    return len(primeList)

# Prime.5: Prime Factorization Function. It outputs a list containing the prime factorization of an inputted number.
def primeFact(n:int) -> list:
    """It outputs a list containing the prime factorization of an inputted number."""
    factors=[]
    primeList=primesBetween(1,n)
    index=0 # Prime List index
    while n>1:
        primeCheck=primeList[index]
        if n%primeCheck==0: # Prime Factor: store in factors, divide n and reset index:
            factors.append(primeCheck)
            index=0; n/=primeCheck
        else: # Not a prime factor: continue loop, add 1 to index
            index+=1

    return factors


# ------------- 'is' Functions -------------
# is.1: isTriangular Function. It outputs whether a number is a triangular number or not.
def isTriangular(n:int) -> bool:
    """It outputs whether a number is a triangular number or not."""
    intCheck(n) # Check if n is positive integer
    
    int_sum=0; i=0
    while int_sum<=n:
        i+=1
        int_sum+=i
        if int_sum==n:
            return True
        
    return False

# is.2: isHexagonal Function. It outputs whether a number is a hexagonal number or not.
def isHexagonal(n:int) -> bool:
    """It outputs whether a number is a hexagonal number or not."""
    intCheck(n) # Check if n is positive integer

    hex_sequence=0; counter=0
    while hex_sequence<=n:
        counter+=1
        hex_sequence+=counter*(2*counter-1)
        if hex_sequence==n:
            return True
        
    return False

# is.3: isNarcissist Function. It outputs whether a number is narcissist or not.
# n is narcissist if the sum of its digits to the length power is equal to itself.
def isNarcissist(n:int) -> bool:
    """
    It outputs whether a number is narcissist or not.
    A number is narcissist if the sum of its digits to the length power is equal to itself.
    """
    intCheck(n) # Check if n is positive integer
    
    l=len(str(n))
    list_digits=[int(i) for i in str(n)]
    result=0
    for i in range(l):
        result+=list_digits[i]**l
    
    if n==result: # Check the condition:
        return True
        
    return False

# is.4: isHarshad Function. It outputs whether a number is a Harshad/Niven number or not.
# n is a Harshad/Niven number if it is divisible by the sum of its digits.
def isHarshad(n:int) -> bool:
    """
    It outputs whether a number is a Harshad/Niven number or not.
    A number is a Harshad/Niven number if it is divisible by the sum of its digits.
    """
    intCheck(n) # Check if n is positive integer
    
    sumDigits=sum([int(i) for i in str(n)])
    if n%sumDigits==0: # Check the condition:
        return True
    
    return False

# is.5 isMunchausen Function. It outputs whether a number is a Munchausen number or not.
# n is a Munchausen number if it is equal to the sum of its digits raised to the power of themselves.
def isMunchausen(n:int) -> bool:
    """
    It outputs whether a number is a Munchausen number or not.
    A number is a Munchausen number if it is equal to the sum of its digits raised to the power of themselves.
    """
    intCheck(n) # Check if n is positive integer
    
    digits=[int(i)**int(i) for i in str(n)]
    if sum(digits)==n:
        return True
    
    return False

# ------------- Proper Math Functions -------------
# PM.1: nth-Root Function. It outputs the n-th root of a given number.
# We use exponential-logarithm form, so floating point precision can be limited.
def nthRoot(n:float,index:int) -> float:
    """
    It outputs the nth root of a given number.
    We use exponential-logarithm form, so floating point precision can be limited.
    """
    intCheck(index) # Check if index is positive integer
    
    if index%2==0 and n>0: # Check positive n if index is even:
        raise InputError("The radicand must be positive for an even index root")
    
    if index%2==1 and n<0: # Odd index and negative radicand:
        return -math.exp((math.log(-n))/index)
    else:
        return math.exp((math.log(n))/index)

# PM.2: Sign Function. It outputs the sign of a given number -> +1 if positive, -1 if negative, 0 if 0.
def sign(n:float) -> int:
    """It outputs the sign of a given number -> +1 if positive, -1 if negative, 0 if 0."""
    if n>0:
        return 1
    elif n<0:
        return -1
    else:
        return 0

# PM.3: Dirac Delta Function. It outputs delta(n), being n the inputted number.
# delta is infinity if x=0, and 0 if it is NOT 0.
def deltaDirac(n:int) -> float:
    """
    It outputs delta(n), being n the inputted number.
    delta is infinity if x=0, and 0 if it is NOT 0.
    """
    if n==0: # Check the condition:
        return float('inf')
    
    return 0

# PM.4: Kronecker Delta Function. It outputs 1 if both numbers are equal, and 0 elsewhere.
def deltaKronecker(i:int,j:int) -> int:
    """It outputs 1 if both numbers are equal, and 0 elsewhere."""
    intCheck(i) # Check if i is positive integer
    intCheck(j) # Check if j is positive integer
    
    if i==j:
        return 1
    
    return 0

# PM.5: Heaviside Step Function. It outputs 1 if x is positive, 1/2 if x is 0, and 0 if x is negative.
def heaviside(x:float) -> float:
    """It outputs the Heaviside Step Function of x, i.e., 1 if x is positive, 1/2 if x is 0, and 0 if x is negative."""
    return (sign(x)+1)/2

# PM.6: Ramp Function. It outputs x if x is positive, 0 elsewhere.
def ramp(x:float) -> float:
    """It outputs x if x is positive, 0 elsewhere."""
    return x*heaviside(x)

# PM.7: Long Division Function. It outputs the quotient and remainder of the operation a/b.
def longDivision(a:int, b:int) -> tuple[int,int]:
    """It outputs the quotient and remainder of the operation a/b."""
    intCheck(a) # Check if a is positive integer
    intCheck(b) # Check if b is positive integer
    
    return a//b , a%b

# PM.8: Subfactorial Function. It outputs the subfactorial of an inputted number (!n).
def subFactorial(n:int) -> int:
    """It outputs the subfactorial of an inputted number (!n)."""
    intCheck(n) # Check if n is positive integer

    f=math.factorial(n)
    adder=0
    for k in range(n+1):
        adder+=(-1)**k / math.factorial(k)
    
    return round(f*adder)

# PM.9: Primordial Function. It outputs the primordial of a given number (n#) i.e., the product of all primes less than n.
def primordial(n:int) -> int:
    """It outputs the primordial of a given number (n#) i.e., the product of all primes less than n."""
    intCheck(n) # Check if n is positive integer
    
    primeList=primesBetween(1,n)
    result=1
    for i in range(len(primeList)):
        result*=primeList[i]

    return result

# PM.10: Decimal Part Function. It outputs the decimal part of a given number.
def decimalPart(n:float) -> float:
    """It outputs the decimal part of a given number."""
    return n-math.floor(n)

# PM.11: Linear Spacing Function. It outputs a list containing n elements equally spaced between a and b.
def linSpace(a:float,b:float,n:int) -> list[float]:
    """It outputs a list containing n elements equally spaced between a and b."""
    intCheck(n) # Check if n is positive integer
    
    if a==b: # The limits are equal -> Division by Zero, raise exception:
        raise InputError("The limits shall not be equal to each other")
    
    #if b<a: # b must be greater than 1 to assure clean division:
    #    raise InputError("The upper limit 'b' must be greater than the lower limit 'a'")

    step=(b-a)/(n-1)
    
    return [a + i * step for i in range(n)]

# PM.12: Discrete Convolution Function. It outputs the discrete convolution of the lists a and b (a*b).
def convolve(x:(list | tuple),y:(list | tuple)) -> tuple:
    """It outputs the discrete convolution of the lists a and b (a*b)."""
    c=[]; a=len(x); b=len(y); # Initialize variables:
    for n in range(a+b-1): # Length of the convolution
        result=0
        for i in range(n+1):
            try:
                result+=x[i]*y[n-i]
            except IndexError:
                pass

        c.append(result)

    return tuple(c)

# ------------- Calculus Functions -------------
# Cal.1: Num. Derivative function. It outputs the numerical derivative of 'f' in the point 'a' with precision 'h'.
def derive(f,a:float,n:int,h:float=None) -> float:
    """It outputs the numerical n-th derivative of 'f' in the point 'a' with precision 'h'.

    By default, h gets set at the best precision possible for the given derivative order."""
    if h==0: # We can't have infinite precision -> raise exception
        raise InputError("Unable to perform operation: cannot operate using infinite precision")
    
    if n<=0 or n!=math.floor(n): # We can't have 0-th derivative, fractional derivatives or negative derivatives -> raise exception
        raise InputError("The 'n' parameter must be an integer greater than 0")
    
    match n:
        case 1:
            # Best precision for 1st Derivative -> h == 1e-4
            if h==None: # No value has been set -> Default value
                h=1e-4
            
            return (-f(a+2*h)+8*f(a+h)-8*f(a-h)+f(a-2*h)) / (12*h)
        case 2:
            # Best precision for 2nd Derivative -> h == 9e-3
            if h==None:
                h=9e-3
            
            return (-f(a-2*h)+16*f(a-h)-30*f(a)+16*f(a+h)-f(a+2*h)) / (12*(h**2))
        case 3:
            # Best precision for 3rd Derivative -> h == 5e-3
            if h==None:
                h=5e-3
            
            return (f(a-3*h)-8*f(a-2*h)+13*f(a-h)-13*f(a+h)+8*f(a+2*h)-f(a+3*h)) / (8*(h**3))
        case 4:
            # Best precision for 4th Derivative -> h == 7e-2
            if h==None:
                h=7e-2
            
            return (-f(a-3*h)+12*f(a-2*h)-39*f(a-h)+56*f(a)-39*f(a+h)+12*f(a+2*h)-f(a+3*h)) / (6*(h**4))
        case _:
            raise InputError("The derive function only takes on 1st, 2nd, 3rd and 4th derivatives.")

# Cal.2: Num. Integral function. It outputs the numeric integral of 'f' in the interval [a,b].
def integral(f,a:float,b:float) -> float:
    """It outputs the numerical integral of 'f' in the interval [a,b].
    We use Boole's Rule for this function (error ~ 6-th derivative)"""

    if b>a: # Coordinates are inverted:
        a, b = b, a # Coordinate Permutation.

    if a==b: # We can't calculate the area under a 0 interval -> return 0
        return 0

    xList=linSpace(a,b,5)
    h=(b-a)/4

    intTerm=(7*f(xList[0])+32*f(xList[1])+12*f(xList[2])+32*f(xList[3])+7*f(xList[4]))

    return (h*2/45) * intTerm

# Cal.3: Fourier Series Function. It outputs the Fourier coefficients of a function 'f' in the interval [a,b] with 'n' iterations.
def fourierSeries(f,a:float,b:float,n:int) -> tuple[float,tuple[float],tuple[float]]:
    """It outputs the Fourier coefficients of a function 'f' in the interval [a,b] with 'n' iterations."""

    intCheck(n) # Check if n is positive integer

    if a==b: # We can't calculate Fourier in the [a,a] interval -> raise exception
        raise InputError("The 'a' and 'b' parameters must be different, with b > a")
    
    if a>b: # Coordinates are permutated:
        a, b = b, a
    
    intFactor = 2 / (b-a)

    a0=intFactor * integral(f,a,b) # Calculate a_0
    an=[]; bn=[] # Initialize a_n and b_n

    for k in range(1,n+1):
        sineMult   = lambda x : f(x) * math.sin(((2*math.pi*k)/(b-a)) * (x-((a+b)/2)))
        cosineMult = lambda x : f(x) * math.cos(((2*math.pi*k)/(b-a)) * (x-((a+b)/2)))

        an.append(intFactor * integral(cosineMult,a,b))
        bn.append(intFactor * integral( sineMult ,a,b))
    
    return (a0,tuple(an),tuple(bn))

# Cal.4: Solve f == 0 Function. It outputs the solution of f==0 using the Newton - Raphson Method.
def solveF(f,start:float,precision:float=1e-6) -> float:
    """It outputs the solution of f==0 using the Newton-Raphson Method.
    'start' is the starting point of the method, 'precision' is the maximum iterative error (default == 1e-6)"""

    error=1e5 # Overestimate the error
    oldPoint=start # Set the starting point
    while error>precision: # If the error is greater than precision -> Continue iterating
        newPoint=oldPoint - (f(oldPoint) / derive(f,oldPoint,1)) # Apply method

        error=math.fabs(newPoint-oldPoint) # Calculate error
        oldPoint=newPoint # Re-Set the points

    return newPoint