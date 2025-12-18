"""
Matrix Module of the library RecMath. It imports the 'matrix' class 
(datatype that imports matrices as a list of lists of real numbers).
"""
class InputError(Exception):
    def __init__(self, *args):
        """This is RecMath's way of saying: you f***ed/messed up"""
        super().__init__(*args)

# "matrix"  class:
# Note: These matrices are bulit using Python Lists -> A matrix is defined as:
# -> A list of nº of files elements, each element being a list with nº of rows elements ---> M[file][row]
# m=matrix() defines an object matrix. With m.zeros(files,rows), you create a matrix stored in m.state

# 4/12/25 -> Added Matrix Convolution
class matrix():
    """
    Matrix class. This datatype is bulit using Python Lists, i.e., a matrix is defined as
    a list of nº of files elements, each element being a list with nº of rows elements ---> M[file][row]
    """
    def __init__(self):
        """
        Matrix class. This datatype is bulit using Python Lists, i.e., a matrix is defined as:
        - A list of nº of files elements, each element being a list with nº of rows elements ---> M[file][row]

        m=matrix() defines an object matrix. With m.zeros(files,rows), you create a matrix stored in m.state.
        """
        pass

    # M.1a: fancy Method. It outputs the self.state matrix in a better console display.
    def fancy(self):
        """It outputs the self.state matrix in a better console display."""
        for i in range(len(self.state)):
            for j in range(len(self.state[0])): # Matrix length is constant
                print(self.state[i][j], end="\t")
            
            print("")
        
        print("")
    
    # M.1b. Element Set Method. It overwrites the element (i,j) in the matrix self.state
    def elementSet(self,pos_files:int,pos_rows:int,n:int):
        """It overwrites the element (i,j) in the matrix self.state"""
        # Check if the positions are bounded:
        if (pos_files<1 or pos_files>len(self.state)) or (pos_rows<1 or pos_rows>len(self.state[0])):
            raise InputError("The positions are not bounded")
        
        self.state[pos_files-1][pos_rows-1]=n

    # M.2: zeros Method. It creates an empty matrix, with 'files' files and 'rows' rows, and stores it in self.state
    def zeros(self,files:int,rows:int=None):
        """It creates an empty matrix, with 'files' files and 'rows' rows, and stores it in self.state"""
        if rows==None: # If no 'rows' argument is given, then the method outputs a square matrix
            rows=files

        self.state=[[0 for i in range(rows)] for i in range(files)]
    
    # M.3: nths Method. It creates a matrix with 'files' files and 'rows' rows, each element being n, and stores it in self.state
    def nths(self,n:int,files:int,rows:int=None):
        """It creates a matrix with 'files' files and 'rows' rows, each element being n, and stores it in self.state"""
        if rows==None: # If no 'rows' argument is given, then the method outputs a square matrix
            rows=files
    
        self.state=[[n for i in range(rows)] for i in range(files)]
    
    # M.4: eye Method. It creates the n-th identity matrix / nxm Hermite normal form, and stores it in self.state
    def eye(self,files:int,rows:int=None):
        """It creates the n-th identity matrix / n x m Hermite normal form, and stores it in self.state"""
        if rows==None: # If no 'rows' argument is given, then the method outputs a square matrix
            rows=files

        it_matrix=matrix()
        it_matrix.zeros(files,rows)
        
        for i in range(files):
            for j in range(rows):
                if i==j:
                    it_matrix.state[i][j]=1
        
        self.state=it_matrix.state

    # M.5: transpose Method. It transposes the self.state matrix, and stores it in mat2.state
    def transpose(self):
        """ It transposes the self.state matrix, and stores it in exit_variable.state"""
        originalFiles=len(self.state); originalRows=len(self.state[0]) # Define coordinates:
        
        mat2=matrix() # Initialize mat2 as a matrix.
        mat2.zeros(originalRows,originalFiles) # We initialize the transposed matrix with the right dimensions:

        for i in range(len(mat2.state)): # We iterate the files
            for j in range(len(mat2.state[0])): # We iterate the rows
                mat2.state[i][j]=self.state[j][i]
        
        return mat2 # It returns the OBJECT, NOT THE MATRIX
    
    # M.6: triangular Method. It creates a triangular matrix based on the self.state matrix and the isUp value (1=UpperTri, 0=LowerTri).
    # The triangular matrix is stored on mat2.state
    def triangular(self,isUp:bool):
        """
        It creates a triangular matrix based on the self.state matrix and the isUp value (1=UpperTri, 0=LowerTri).
        The triangular matrix is stored on exit_variable.state
        """
        files=len(self.state); rows=len(self.state[0]) # Define coordinates:

        if files!=rows: # The matrix is NOT SQUARE: raise exception
            raise InputError("The inputted matrix must be square")
        
        mat2=matrix()
        mat2.state=self.state()
        
        if isUp==True: # We want the Upper Triangular Matrix:
            for i in range(files): # We iterate the files
                for j in range(rows): # We iterate the rows
                    if i>j:
                        mat2.state[i][j]=0
        else: # We want the Lower Triangular Matrix:
            for i in range(files): # We iterate the files
                for j in range(rows): # We iterate the rows
                    if j>i:
                        mat2.state[i][j]=0
        
        return mat2 # It returns the OBJECT, NOT THE MATRIX
    
    # M.7: diag Method. It creates a square matrix with the inputted list in its main diagonals, and stores it on self.state
    def diag(self,vector:list,diag_number:int=0):
        """It creates a square matrix with the inputted list in its main diagonals, and stores it on self.state"""
        self.state=self.zeros(len(vector)+abs(diag_number))

        counter=0
        files=len(self.state); rows=len(self.state[0]) # Define coordinates

        for i in range(files):
            for j in range(rows):
                if i-j==-diag_number: # Choose diagonal:
                    self.state[i][j]=vector[counter]
                    counter+=1

    # M.8: trace Method. It outputs the trace of the self.state matrix.
    def trace(self) -> float:
        """It outputs the trace of the self.state matrix."""
        files=len(self.state); rows=len(self.state[0]) # Define coordinates:

        if files!=rows: # The matrix is NOT SQUARE: raise exception
            raise InputError("The inputted matrix must be square")
        
        tr=0 # Initialize 'tr'
        for i in range(files):
            tr+=self.state[i][i]

        return tr # We return the value of the trace:
    
    # M.9: addSubtract Method. It outputs the sum/difference between self.state and other.state matrices (depending on the isSum argument)
    # The result matrix is stored on result_matrix.state
    def addSubtract(self,other,isSum:bool):
        """
        It outputs the sum/difference between self.state and other.state matrices (depending on the isSum argument)
        The result matrix is stored on exit_variable.state
        """
        files1=len(self.state); rows1=len(self.state[0])
        files2=len(other.state); rows2=len(other.state[0])

        if files1!=files2 or rows1!=rows2: # The dimensions do not match -> raise exception
            raise InputError("The dimensions of the inputted matrices NEED TO BE EQUAL")
        
        result_matrix=matrix() # We initialize the return matrix
        result_matrix.zeros(files1,rows1) 

        if isSum==True: # We want the sum:
            for i in range(files1):
                for j in range(rows1):
                    result_matrix.state[i][j]=self.state[i][j]+other.state[i][j]
        else: # We want the difference:
            for i in range(files1):
                for j in range(rows1):
                    result_matrix.state[i][j]=self.state[i][j]-other.state[i][j]

        return result_matrix
    
    # M.10: singleOperator Method. It outputs the opposite/absolute value of the self.state matrix.
    # The result matrix is stored on result_matrix.state:
    def singleOperator(self,isOpp:bool):
        """
        It outputs the opposite/absolute value of the self.state matrix.
        The result matrix is stored on exit_variable.state:
        """
        files=len(self.state); rows=len(self.state[0])

        result_matrix=matrix() # We initialize the return matrix
        result_matrix.zeros(files,rows)

        if isOpp==True: # We want the opposite of the input matrix:
            for i in range(files):
                for j in range(rows):
                    result_matrix.state[i][j]=-self.state[i][j]
        else:
            for i in range(files):
                for j in range(rows):
                    result_matrix.state[i][j]=abs(self.state[i][j])
        
        return result_matrix
    
    # M.11: scalarMult Method. It outputs the scalar multiplication of the self.state matrix and an inputted scalar.
    # The result matrix is stored on result_matrix.state:
    def scalarMult(self,scalar:float):
        """
        It outputs the scalar multiplication of the self.state matrix and an inputted scalar.
        The result matrix is stored on exit_variable.state
        """
        files=len(self.state); rows=len(self.state[0])

        result_matrix=matrix() # We initialize the return matrix
        result_matrix.zeros(files,rows)

        for i in range(files):
            for j in range(rows):
                result_matrix.state[i][j]=scalar*self.state[i][j]
        
        return result_matrix
    
    # M.12: matrixMult Method. It outputs the matrix product A*B, A and B being 2 inputted matrices.
    # The result matrix is stored on result_matrix.state:
    def matrixMult(self,other):
        """
        It outputs the matrix product A*B, A and B being 2 inputted matrices.
        The result matrix is stored on exit_variable.state
        """
        files1=len(self.state); rows1=len(self.state[0])
        files2=len(other.state); rows2=len(other.state[0])

        if rows1!=files2: # Necessary condition
            raise InputError("The dimensions don't match")
        
        result_matrix=matrix()
        result_matrix.zeros(files1,rows2)


        for i in range(files1):
            for j in range(rows2):
                # Computing element[i][j]
                it_variable=0

                for k in range(files2):
                    it_variable+=(self.state[i][k]*other.state[k][j])
                
                result_matrix.state[i][j]=it_variable

        return result_matrix
    
    # M.13: Matrix Convolution Method. It outputs the matrix convolution of self and B (both being matrices of the same dimension).
    def matConvolute(self,y) -> float:
        """It outputs the matrix convolution of self and B (both being matrices of the same dimension)
        The matrix convolution is an operation that takes two matrices A and B and outputs a *number* A*B."""
        colM1=len(self.state); fileN1=len(self.state[0])
        colM2=len(y.state); fileN2=len(y.state[0])

        if colM1!=colM2 or fileN1!=fileN2: # The dimensions do not match
            raise InputError("Unable to do convolution: matrix dimensions do not match")
        
        m=colM1; n=fileN2
        result=0

        for i in range(m):
            for j in range(n):
                result+=(self.state[(m-i)-1][(n-j)-1] * y.state[(1+i)-1][(1+j)-1])

        return result