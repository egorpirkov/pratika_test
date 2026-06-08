def validate_password(password: str) -> bool:
    if not isinstance(password, str):
        return False
        
    if len(password) < 8:
        return False
        
    if " " in password:
        return False
        
    has_letter = any(char.isalpha() for char in password)
    has_digit = any(char.isdigit() for char in password)
    
    return has_letter and has_digit


def filter_positive_numbers(input_list):
    if not isinstance(input_list, list):
        raise TypeError("Входные данные должны быть списком")
        
    result = []
    
    for item in input_list:
        if isinstance(item, (int, float)) and not isinstance(item, bool):
            if item > 0:
                result.append(item)
                
    return result