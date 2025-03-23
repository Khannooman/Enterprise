import random
import string

def generate_invoice_number() -> str:
    """
    Generate a 10-digit alphanumeric invoice number starting with 'ER'.
    
    Format: ERXXXXXXXX (where X is an uppercase letter or digit)
    Length: 10 characters
    Example: ER7K9P2MX4N
    
    Returns:
        str: A unique 10-character invoice number
    """
    prefix = "ER"
    characters = string.ascii_uppercase + string.digits  # A-Z, 0-9
    random_part = ''.join(random.choice(characters) for _ in range(8))  # 8 random characters
    return prefix + random_part

# Example usage
if __name__ == "__main__":
    for _ in range(5):  # Generate 5 sample invoice numbers
        invoice_number = generate_invoice_number()
        print(f"Generated Invoice Number: {invoice_number}, Length: {len(invoice_number)}")