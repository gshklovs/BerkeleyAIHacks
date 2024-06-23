def merge_requirements(file1, file2, output_file):
    # Read the contents of the first file
    with open(file1, "r") as f1:
        requirements1 = f1.readlines()

    # Read the contents of the second file
    with open(file2, "r") as f2:
        requirements2 = f2.readlines()

    # Combine the requirements
    combined_requirements = requirements1 + requirements2

    # Remove duplicates and sort
    unique_requirements = sorted(set(combined_requirements))

    # Write the combined requirements to the output file
    with open(output_file, "w") as output:
        output.writelines(unique_requirements)


# Define your input and output file names
file1 = "requirements.txt"
file2 = "requirements-greg.txt"
output_file = "merged-requirements.txt"

# Call the function to merge the requirements
merge_requirements(file1, file2, output_file)

print(f"Requirements have been merged into {output_file}")
