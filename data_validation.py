import click


def click_validation(validation_function):
    def callback_validation_function(ctx, param, value):
        is_valid, result = validation_function(value)

        if is_valid:
            return result
        else:
            raise click.BadParameter(result)

    return callback_validation_function


def username_validation(username: str):
    if not username.isalnum():
        return (False, "Must be an alphanumeric string. No special caracter allowed.")
    if len(username) > 30:
        return (False, "Must be 30 caracters or less.")

    return (True, username)
