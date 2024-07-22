from itertools import product, chain

def parse_search_string(search_string):
    def decompose(string):
        '''function to decompose the search string into its components'''

        stack = [] # stack to hold nested groups
        current = [] # current group being built
        i = 0 # index to iterate over the string

        while i < len(string):
            if string[i] == '(': # start
                stack.append(current)
                current = []
            elif string[i] == ')': # end
                last = current
                current = stack.pop() # retrieve the parent group
                current.append(last) # add the closed group to the parent
            elif string[i:i+3] == "AND": # Logical AND operator
                current.append("AND")
                i += 2
            elif string[i:i+2] == "OR": # Logical OR operator
                current.append("OR")
                i += 1
            elif string[i] == '"' or string[i] == "'":  # check for both double and single quotes
                j = i + 1

                while j < len(string) and string[j] != '"' and string[j] != "'":  # find the end of the quoted string
                    j += 1

                current.append(string[i+1:j].replace('"', ''))  # remove double quotes if any
                i = j

            i += 1 # move to the next character
        return current

    def generate_combinations(parsed):
        '''function to generate all possible combinations of the parsed components'''
        if "AND" in parsed:
            and_parts = [part for part in parsed if part not in ["AND", "OR"]]  # extract operands excluding operators
            # generate combinations for AND parts
            and_combinations = list(product(*[generate_combinations(part) if isinstance(part, list) else [[part]] for part in and_parts]))
            return [list(chain(*combs)) for combs in and_combinations]  # flatten the combinations
        elif "OR" in parsed:
            or_parts = [part for part in parsed if part not in ["AND", "OR"]]  # exclude operators when generating combinations
            or_combinations = []
            for part in or_parts:
                if isinstance(part, list):
                    or_combinations.extend(generate_combinations(part)) # recursively generate combinations for OR parts
                else:
                    or_combinations.append([part]) # single operand becomes a list containing itself
            return or_combinations
        else:
            return [parsed]  # Base case: return the parsed components as a single combination

    # convert the parsed string into combinations
    parsed_string = decompose(search_string)
    # generate all possible combinations of the parsed components
    combinations = generate_combinations(parsed_string)

    return combinations

def process_file(file_path):
    '''function to read and process each line (test case) from a file'''

    test_case_count = 0 # counter
    with open(file_path, 'r') as file:
        for line in file:
            search_string = line.strip()
            if search_string:
                output = parse_search_string(search_string)
                total_combinations = len(output)
                print(f'Test Case {test_case_count + 1}:')
                print(f'Input: {search_string}')
                print(f'Output: {output}') # comment this when uncommenting the next 3 lines
                # print('Output:') # uncomment these 3 lines for pretty print
                # for combination in output:
                #     print(['"' + str(item).replace('"', '') + '"' if isinstance(item, str) else item for item in combination])
                print(f'Total Combinations: {total_combinations}\n')

                test_case_count += 1 # increment

if __name__ == '__main__':
    file_path = 'search_strings.txt'
    process_file(file_path)
