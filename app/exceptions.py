class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, resource: str, resource_id: int):
        message = f"{resource} with id {resource_id} not found"
        super().__init__(message=message, status_code=404)


class EmptyCartException(AppException):
    def __init__(self):
        super().__init__(
            message="Cannot checkout an empty cart",
            status_code=400
        )


class CartAlreadyCheckedOutException(AppException):
    def __init__(self, cart_id: int):
        message = f"Cart with id {cart_id} is already checked out"
        super().__init__(message=message, status_code=400)


class DuplicateItemException(AppException):
    def __init__(self, prod_id: int):
        message = f"Product with id {prod_id} already exists in cart"
        super().__init__(message=message, status_code=409)
