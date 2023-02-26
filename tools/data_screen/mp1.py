import multiprocessing

# Create a shared dictionary
data_sock = multiprocessing.Manager().dict({
    "Driver1": {
        "name": "asd asd",
        "time": "0"
    },
    "Driver2": {
        "name": "asdasd asd",
        "time": "0"
    }
})

# Define a function that modifies the dictionary
def update_dict():
    data_sock["Driver1"]["time"] = "1"
    data_sock["Driver2"]["time"] = "2"

# Create a process that modifies the dictionary
p = multiprocessing.Process(target=update_dict)

# Start the process
p.start()

# Wait for the process to finish
input()
p.join()

# Print the modified dictionary
print(data_sock)