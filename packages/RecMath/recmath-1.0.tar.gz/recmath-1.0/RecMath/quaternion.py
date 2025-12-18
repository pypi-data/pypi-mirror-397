"""
Quaternion Module of the library RecMath. It imports the 'quaternion' class 
(datatype that imports quaternions as a collection of ordered numbers.
"""
import math
from RecMath import vector

class InputError(Exception):
    def __init__(self, *args):
        """This is RecMath's way of saying: you f***ed/messed up"""
        super().__init__(*args)

class quaternion():
    """4D Quaternion Objects. This datatype works the same as a real life quaternion would do."""
    def __init__(self):
        """4D Quaternion Objects. This datatype works the same as a real life quaternion would do."""
        self.real=0 # Initialize real component
        self.i=0; self.j=0; self.k=0 # Initialize vector component
    
    # Q.1: fancy Method. It outputs the self quaternion in a better console display.
    def fancy(self):
        """It outputs the quaternion self in a better console display."""
        sign_i="+"; sign_j="+"; sign_k="+"
        exit_i=self.i; exit_j=self.j; exit_k=self.k
        if self.i<0:
            sign_i="-"; exit_i=-self.i
        if self.j<0:
            sign_j="-"; exit_j=-self.j
        if self.k<0:
            sign_k="-"; exit_k=-self.k
        
        print(f"{self.real} {sign_i} {exit_i}i {sign_j} {exit_j}j {sign_k} {exit_k}k")
    
    # Q.2: Module Method. It outputs the module of the quaternion self.
    def norm(self) -> float:
        """It outputs the module/norm of the quaternion self."""
        return math.sqrt(self.real**2 + self.i**2 + self.j**2 + self.k**2) # Square root

    # Q.3: Normalize Method. It normalizes the self quaternion, and stores it in q2.
    def normalize(self):
        """It normalizes the self quaternion (||q||=1), and stores it in exit_variable."""
        mod=self.norm()
        q2=quaternion()

        q2.real=self.real/mod
        q2.i=self.i/mod; q2.j=self.j/mod; q2.k=self.k/mod

        return q2

    # Q.4: Conjugate Method. It outputs the conjugate of self, and stores it in q_res.
    def conj(self):
        """It outputs the conjugate of self, and stores it in exit_variable."""
        q_res=quaternion()

        q_res.real=self.real # Real part does not change
        q_res.i=-self.i
        q_res.j=-self.j
        q_res.k=-self.k

        return q_res

    # Q.5: Sum Method. It outputs the sum of self and q2, and stores it in q_res.
    def sum(self,q2):
        """It outputs the sum of self and q2, and stores it in exit_variable."""
        q_res=quaternion()
        
        q_res.real=self.real+q2.real
        q_res.i=self.i+q2.i
        q_res.j=self.j+q2.j
        q_res.k=self.k+q2.k

        return q_res

    # Q.6: Subtract Method. It outputs self - q2 and stores it in q_res.
    def subtract(self,q2):
        """It outputs self - q2, and stores it in exit_variable."""
        q_res=quaternion()
        
        q_res.real=self.real-q2.real
        q_res.i=self.i-q2.i
        q_res.j=self.j-q2.j
        q_res.k=self.k-q2.k

        return q_res
    
    # Q.7: Scalar Multiplication Method. It outputs the scalar product between n and self, and stores it in q_res.
    def scalarMult(self,n:int):
        """It outputs the scalar product between n and self, and stores it in exit_variable."""
        q_res=quaternion()

        q_res.real= n * self.real
        q_res.i= n * self.i
        q_res.j= n * self.j
        q_res.k= n * self.k

        return q_res

    # Q.8: Product Method. It outputs the product between self and q2, and stores it in q_res.
    def product(self,q2):
        """
        It outputs self * q2 (IN THAT ORDER!!), and stores it in exit_variable.
        We use the scalar-vector multiplication for this method.
        """
        # Initial definitions:
        scalar_self=self.real; list_vector_self=[self.i,self.j,self.k]
        scalar_q2=q2.real; list_vector_q2=[q2.i,q2.j,q2.k]

        vector_self=vector.vector(length=1); vector_self.vectorSet(list_vector_self)
        vector_q2=vector.vector(length=1); vector_q2.vectorSet(list_vector_q2)

        scalar_result=(scalar_self*scalar_q2)-(vector_self.dot(vector_q2)) # Scalar Part
        
        cross_product=vector_self.cross(vector_q2)
        sum1_vector=vector_q2.scalarMult(scalar_self)
        sum2_vector=vector_self.scalarMult(scalar_q2)

        # Vector part using lists, as the 'sum' method blew up XD
        result_list=[sum1_vector.state[i]+sum2_vector.state[i]+cross_product.state[i] for i in range(3)]

        # Once all of the arithmetic has been done, redo the result quaternion:

        q_res=quaternion()

        q_res.real=scalar_result
        q_res.i=result_list[0]
        q_res.j=result_list[1]
        q_res.k=result_list[2]

        return q_res
        
    # Q.9: Inverse Method. It outputs the inverse of the quaternion self, and stores it in q_res.
    def inverse(self):
        """It outputs the inverse of the quaternion self, and stores it in exit_variable."""
        denominator=(self.norm())**2
        if denominator==0: # We input the zero quaternion: raise exception:
            raise InputError("The quaternion inputted has no inverse (zero quaternion)")

        q_res=quaternion()
        conjugate=self.conj()
        
        q_res.real=conjugate.real/denominator
        q_res.i=conjugate.i/denominator
        q_res.j=conjugate.j/denominator
        q_res.k=conjugate.k/denominator

        return q_res
        
    # Q.10: Division Method: It outputs self * q2^-1 or q2^-1 * self, and stores it in q_res.
    def division(self,q2,isLeft:bool):
        """
        It outputs the division between self and q2, and stores it in exit_variable.
        The executed operation depends on the isLeft argument:
        - isLeft == True -> Left Division -> q2^-1 * self
        - isLeft == False -> Right Division -> self * q2^-1
        """
        q_res=quaternion()
        left_mult=quaternion(); right_mult=quaternion()
        denominator=q2.norm() ** 2

        if isLeft==True: # Left division: q2^-1 * self
            left_mult=q2.conj()
            right_mult=self
        else: # Right division: self * q2^-1
            left_mult=self
            right_mult=q2.conj()

        q_res=left_mult.product(right_mult)

        q_res.real/=denominator
        q_res.i/=denominator
        q_res.j/=denominator
        q_res.k/=denominator

        return q_res
    
    # Q.11: Exponential Method. It outputs exp(self), and stores it in q_res.
    def exp(self):
        """It outputs exp(self), and stores it in exit_variable."""
        q_res=quaternion()
        mult_factor=math.exp(self.real)

        vectorPart_module=math.sqrt(self.i ** 2 + self.j ** 2 + self.k ** 2)
        cosine_mod=math.cos(vectorPart_module)
        sine_mod=math.sin(vectorPart_module)
        sine_mult=sine_mod/vectorPart_module

        q_res.real=mult_factor * cosine_mod
        q_res.i=self.i * mult_factor * sine_mult
        q_res.j=self.j * mult_factor * sine_mult
        q_res.k=self.k * mult_factor * sine_mult
        
        return q_res
    
    # Q.12: Logarithm Method. It outputs ln(self), and stores it in q_res.
    def quaternicLog(self):
        """It outputs ln(self), and stores it in exit_variable"""
        q_res=quaternion()
        vectorPart_module=math.sqrt(self.i ** 2 + self.j ** 2 + self.k ** 2)
        module=self.norm()

        vectorMult_part=math.acos(self.real / module)

        q_res.real=math.log(module)
        q_res.i=self.i * vectorMult_part / vectorPart_module
        q_res.j=self.j * vectorMult_part / vectorPart_module
        q_res.k=self.k * vectorMult_part / vectorPart_module

        return q_res