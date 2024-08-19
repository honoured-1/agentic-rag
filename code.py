python
def add_numbers(num1, num2):
  """
  This function adds two numbers together.

  Args:
    num1: The first number.
    num2: The second number.

  Returns:
    The sum of the two numbers.
  """

  try:
    # Convert the inputs to floats to handle potential decimal numbers
    num1 = float(num1)
    num2 = float(num2)
    return num1 + num2
  except ValueError:
    # Handle cases where the inputs are not valid numbers
    return "Invalid input. Please enter valid numbers."

# Get input from the user
num1 = input("Enter the first number: ")
num2 = input("Enter the second number: ")

# Call the add_numbers function and print the result
result = add_numbers(num1, num2)
print(f"The sum of {num1} and {num2} is: {result}")
