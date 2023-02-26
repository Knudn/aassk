import multiprocessing

# Create a Manager object
manager = multiprocessing.Manager()

# Access the shared dictionary
data_sock = manager.dict()

# Print the initial contents of the dictionary
print(data_sock)

# Wait for input from the user
input("Press Enter to continue...")


# Print the modified dictionary
print(data_sock)