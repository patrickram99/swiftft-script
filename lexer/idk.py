def main():
    dictionary = {}
    dictionary["learning"] = "awesome"
    dictionary["coding"] = "fun"
    dictionary["learn"] = "CRY"
    dictionary["learn"] = "CRY2"
    remove_keys_containing_string(dictionary, "learn")

    for key in dictionary:
        print(dictionary[key])

"""
This Python function takes in a dict and a string and  
removes all keys containing that string from the dict
"""
def remove_keys_containing_string(dictionary, remove):
    new_dictionary = {}
    for key in dictionary:
        if remove not in key:
            new_dictionary[key] = dictionary[key]

if __name__ == "__main__":
    main()

