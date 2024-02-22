import numpy as np

# These variables are declared globally
# to save time for reallocation of memory
# every time sorting function is called
indices = np.arange(1)
vector_element_indices = np.arange(1)
p, q = np.meshgrid(indices, indices, indexing='ij')
ret_indices = np.zeros(1, dtype=int)
n = m = d = 1

def set_dimensions(num_vector, max_return_size, vector_dim) :
    ''' Adjusts global variables if input shape of vectors
        gets changed    '''
    
    global p, q, ret_indices, indices, vector_element_indices, n, m, d
    
    if n != num_vector :
        
        indices = np.arange(num_vector)
        p, q = np.meshgrid(indices, indices, indexing='ij')
        n = num_vector

    if m != max_return_size :
        
        ret_indices = np.zeros(max_return_size, dtype=int)
        m = max_return_size

    if d != vector_dim :

        vector_element_indices = np.arange(d)
        d = vector_dim

    pass

def select_from_same_rank(vectors, num_to_select) :
    ''' Returns the indices in vectors that should be selected
        from a group of vectors with same rank based on
        crowding distance   '''

    global vector_element_indices

    # num_vectors, size_vector = vectors.shape

    # Holds the crowding distance for each vector
    distances = np.zeros(vectors.shape[0])

    # For each dimension i of the vectors

    # i th column holds the indices of vectors in ascending order
    # of values in i th dimension of the vectors
    sorted_indices = np.apply_along_axis(np.argsort, 0, vectors)

    # Setting crowding distance of points at
    # either ends of the spectrum to infinity
    distances[sorted_indices[0]] += np.inf
    distances[sorted_indices[-1]] += np.inf

    # i th value in Delta holds range of values in i th dimension of the vectors
    Delta = vectors[sorted_indices[-1], vector_element_indices] - vectors[sorted_indices[0], vector_element_indices]

    if np.any(Delta==0) :
        # To avoid divide by zero error
        # All vectors will have crowding distance infinity
        # Any of the vectors could be chosen
        return np.arange(num_to_select)

    else :
        # Set the crowding distance for 
        # vectors in between the spectrum
        distances[sorted_indices[1:-1]] += ( vectors[sorted_indices[2:], vector_element_indices] - vectors[sorted_indices[:-2], vector_element_indices] ) / Delta

    # The above code is parallelized version of the 
    # following commented code 
    '''
    for i in range(size_vector) :
        # For each dimension i of the vectors

        # Holds the indices of vectors in ascending order
        # of values in i th dimension of the vectors
        sorted_indices = np.argsort(vectors[:, i])

        # Setting crowding distance of points at
        # either end of the spectrum to infinity
        distances[sorted_indices[0]] += np.inf
        distances[sorted_indices[-1]] += np.inf

        # Range of values in i th dimension of the vectors
        Delta = vectors[sorted_indices[-1], i] - vectors[sorted_indices[0], i]

        if Delta == 0 :
            # Check to prevent divide by zero error in next step
            distances[sorted_indices[1:-1]] += np.inf

        else :
            # Set the crowding distance for 
            # vectors in between the spectrum
            distances[sorted_indices[1:-1]] += ( vectors[sorted_indices[2:], i] - vectors[sorted_indices[:-2], i] ) / Delta
    '''

    # Get indices of vectors in ascending order
    # of their crowding distance
    sorted_indices = np.argsort(distances)
        
    # Return the indices to last num_to_select vectors
    # from the list sorted in ascending order
    # print(vectors)
    # print(vectors[sorted_indices[-num_to_select:]])
    return sorted_indices[-num_to_select:]

def sort_vectors(vectors, max_return_size) :
    ''' Returns the Non Dominating Sorted indices and 
        the number of elements in the Pareto front
        Input vectors should numpy.ndarray of the shape
        (number of vectors, dimension of each vector)
        Input max_return_size specifies the 
        number of top rank vectors required  '''

    global p, q, ret_indices

    num_vector, vector_dim = vectors.shape

    set_dimensions(num_vector, max_return_size, vector_dim)
    
    P, Q = vectors[p], vectors[q]
    # The above statement is equivalent to creating following matrices
    #   for i in range(num_vector)  :      
    #       for j in range(num_vector)  :
    #           P[i,j] = vectors[i]
    #           Q[i,j] = vectors[j]
    
    domination_matrix = np.all(np.greater(P, Q), axis=2)
    # The i,j element of domination matrix holds the truth value
    # whether P[i,j] = vectors[i] dominates Q[i,j] = vectors[j]

    # Holds number of top rank vectors found so far
    num_top_rank_vectors = 0

    # Holds truth value corresponding to each vector
    # whether to consider that vector for domination counting
    consider_vectors = np.ones(num_vector, dtype=bool)

    # Holds number of vectors that dominate vector[i]
    domination_counter = np.sum(domination_matrix, axis=0)

    # Holds indices of vectors that are currently dominated by no one
    vectors_at_curr_rank = np.where(domination_counter==0)[0]

    # print(vectors_at_curr_rank)

    num_vectors_Pareto_front = max_return_size if vectors_at_curr_rank.shape[0] > max_return_size else vectors_at_curr_rank.shape[0]

    # print(domination_counter)
    # print(domination_matrix)
    # print(P, Q)
    # print(vectors)

    while vectors_at_curr_rank.shape[0] + num_top_rank_vectors < max_return_size :

        # Fill the rank list
        # From the number of vectors filled so far
        # To number of vectors that will be filled after 
        # adding vectors at the current rank
        ret_indices[num_top_rank_vectors : num_top_rank_vectors + vectors_at_curr_rank.shape[0]] = vectors_at_curr_rank
        num_top_rank_vectors += vectors_at_curr_rank.shape[0]

        # From here on the vectors in current rank
        # would not be needed to find vectors in the next rank
        consider_vectors[vectors_at_curr_rank] = False

        # Holds number of vectors that dominate vector[i]
        domination_counter = np.sum(domination_matrix[consider_vectors, :], axis=0)

        # Holds indices of vectors that are currently dominated by no one
        vectors_at_curr_rank = np.nonzero(np.bitwise_and(consider_vectors, domination_counter==0))[0]

        # print('Number of Vectors in Current Rank :', vectors_at_curr_rank.shape[0])
        # print('Number of Top Rank Vectors found :', num_top_rank_vectors)
        # print('Vectors at Current Rank :', vectors[ret_indices])
        # print(max_return_size)


    if vectors_at_curr_rank.shape[0] + num_top_rank_vectors == max_return_size :
        # If number of vectors in the last rank exactly fills 
        # the complete sorted list
        ret_indices[num_top_rank_vectors : num_top_rank_vectors + vectors_at_curr_rank.shape[0]] = vectors_at_curr_rank
        num_top_rank_vectors += vectors_at_curr_rank.shape[0]

    else :

        ret_indices[num_top_rank_vectors :] = vectors_at_curr_rank[select_from_same_rank(vectors[vectors_at_curr_rank], max_return_size - num_top_rank_vectors)]

    return num_vectors_Pareto_front, np.copy(ret_indices)

if __name__ == "__main__":
    
    A = np.random.rand(10, 2)

    n, indices = sort_vectors(A, 8)

    print('\nA')
    print(A)
    print('\nSorted A')
    print(A[indices])
    print('\nNumber of vectors in Pareto front :', n)
    # print(np.sum(np.all(np.greater(A[p], A[q]), axis=2), axis=0))

    pass
        





