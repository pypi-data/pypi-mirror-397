"""
Vector Module of the library RecMath. It imports the 'vector' class 
(datatype that imports vectors as an n-th tuple of real numbers).
"""
import math

class InputError(Exception):
    def __init__(self, *args):
        """This is RecMath's way of saying: you f***ed/messed up"""
        super().__init__(*args)

# "Vector" objects:
# Initializing vectors -> v=vector(length='number') -> With this command, a vector of 'number' elements is stored as a tuple in self.state
class vector(tuple):
    """Vector Class. This datatype works exactly the same as a real life 'length' dimensional vector."""
    # V.0a: init Method. It initializes the vector object, generating a tuple of 'length' elements.
    def __init__(self,length:int):
        """Vector Class. This datatype works exactly the same as a real life 'length' dimensional vector."""
        in_list=[0 for i in range(length)]

        self.state=tuple(in_list)
        self.length=len(in_list)

    # V.0b: Vector Set Method. It overwrites the self.state vector in favour of the inputted list.
    def vectorSet(self,new_list:list):
        """It overwrites the self.state vector in favour of the inputted list."""
        self.state=tuple(new_list)
        self.length=len(new_list)

    # V.1: Module Method. It outputs the module of the vector self.state
    def module(self) -> float:
        """It outputs the module of the vector self.state"""
        result=0 # Initialize variable 'result'

        for i in range(self.length):
            result+=((self.state[i])**2)
        
        return (result)**(1/2) # Square root

    # V.2: Normalize Vector Method. It normalizes the self.state vector, and stores it in vct.state
    def normalize(self):
        """It normalizes the self.state vector (|v|=1), and stores it in exit_variable.state"""
        mod=self.module()
        iterable_list=[(self.state[i])/mod for i in range(self.length)] # We use list comprehension

        vct=vector(length=1) # Initialize the object vector 'vct':
        vct.vectorSet(iterable_list)

        return vct # We return the OBJECT, not the vector (Object -> vct ; Vector -> vct.state)

    # V.3: Sum Method. It outputs self.state + vct.state vector, and stores it in result.state
    def sum(self,vct):
        """It outputs self.state + vct.state vector, and stores it in exit_variable.state"""
        if self.length!=vct.length: # The dimensions do not match:
            raise InputError("The dimensions do not match")
        
        result=vector(length=1) # Initialize the object vector 'result':

        it_list=[self.state[i]+vct.state[i] for i in range(self.length)] # Use list comprehension
        result.vectorSet(it_list)

        return result
    
    # V.4: Subtract Method. It outputs self.state - vct.state vector, and stores it in result.state
    def subtract(self,vct):
        """It outputs self.state - vct.state vector, and stores it in exit_variable.state"""
        if self.length!=vct.length: # The dimensions do not match:
            raise InputError("The dimensions do not match")
        
        result=vector(length=1) # Initialize the object vector 'result':

        it_list=[self.state[i]-vct.state[i] for i in range(self.length)] # Use list comprehension
        result.state=tuple(it_list)

        return result
    
    # V.5: Scalar Multiplication Method. It outputs k * self.state, and stores it in result.state
    def scalarMult(self,k:float):
        """It outputs k * self.state, and stores it in exit_variable.state"""
        result=vector(length=1) # Initialize the object vector 'result':

        it_list=[k*self.state[i] for i in range(self.length)] # Use list comprehension
        result.state=tuple(it_list)

        return result
    
    # V.6: Dot Product Method. It outputs the dot product between self.state and vct.state.
    def dot(self,vct) -> float:
        """It outputs the dot product between self.state and vct.state."""
        if self.length!=vct.length: # The dimensions do not match:
            raise InputError("The dimensions do not match")

        result=0 # Initialize the variable 'result':

        for i in range(self.length):
            result+=(self.state[i]*vct.state[i])

        return result
    
    # V.7: Angle Between Vectors Method. It outputs the angle between self.state vector and vct.state vector
    def angleBetween(self,vct,radians:bool=None) -> float:
        """It outputs the angle (in radians unless specified) between self.state vector and vct.state vector"""
        if self.length!=vct.length: # The dimensions do not match:
            raise InputError("The dimensions do not match")
        
        mod_self=self.module(); mod_vct=vct.module()
        dot_product=self.dot(vct)

        result=math.acos(dot_product/(mod_self*mod_vct))

        if radians!=None and radians==False: # We want the result in degrees:
            return result*(180/math.pi)
        
        return result

    # V.8: Cross Product Method. It outputs the 3D cross product of self.state and vct.state vector, and stores it in result.state:
    def cross(self,vct):
        """It outputs the 3D cross product of self.state and vct.state vector, and stores it in exit_variable.state:"""
        if self.length!=3 or vct.length!=3: # The dimensions do not match OR the dimensions are NOT 3:
            raise InputError("The dimensions do not match: must be equal to 3")

        # Calculate cross product coordinates:
        w0=self.state[1]*vct.state[2]-(self.state[2]*vct.state[1])
        w1=self.state[2]*vct.state[0]-(self.state[0]*vct.state[2])
        w2=self.state[0]*vct.state[1]-(self.state[1]*vct.state[0])

        w=(w0,w1,w2) # Create vector:
        result=vector(length=1) # Initialize object vector

        result.vectorSet(w)

        return result

    # V.9: Mixed Product Method. It outputs the 3D mixed product of self.state, v1.state and v2.state, and stores it in result.state:
    def mixed(self,v1,v2) -> float:
        """It outputs the 3D mixed product of self.state, v1.state and v2.state, and stores it in exit_variable.state:"""
        if self.length!=3 or v1.length!=3 or v2.length!=3: # The dimensions do not match OR the dimensions are NOT 3:
            raise InputError("The dimensions do not match: must be equal to 3")

        cross_v=vector(length=3) # Initialize object vector for the cross product
        result=vector(length=3) # Initialize object vector for the mixed product

        cross_v=v1.cross(v2) # We cross v1 and v2 -> v1 x v2
        result=self.dot(cross_v) # We dot the result -> self . (v1 x v2)

        return result