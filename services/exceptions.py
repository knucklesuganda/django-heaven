

class ServiceException(ValueError):
    """
    That is the exception raised by any function from the BaseService()
    when something bad happens because of the normal query, but something in the database.
    """


class ServiceProgrammingException(SyntaxError):
    """
    That is the exception raised when you have a problem with your code, not user related.
    For example, you forgot to provide arguments in model get() function.
    """
