from  src.checks.file_validation_checks import FileValidator

file_path = "/src/data/products.csv"  # Update this with your file path
validator = FileValidator(file_path)

if validator.validate_file():
    print(f"File '{file_path}' passed all validation checks.")
else:
    print(f"File '{file_path}' failed validation.")

print(validator.validate_file_size())