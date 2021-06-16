def get_department_id(e_departments, user):
    """Finds the ID of the eloomi department, for the user, if it does not exist it returns -1

    Args:
        e_departments (Dict): [description]
        user (Dict): [description]

    Returns:
        Int: deparmtent id, or -1 
    """
    try:
        # fetches the department name from the databse checks if it exists
        # in the departments up in eloomi, if it exists returns it
        return e_departments["{}-{}".format(user['mfld'].strip(), user['department'].strip())]['id']
    except KeyError:
        # sometimes the user doesn't have a valid department in it's column
        # so we return -1 instead
        return -1

def get_department_by_name(departments, name):
    """Finds the eloomi department by name

    Args:
        departments (Dict): Dict of all departments in eloomi
        name (Str): Name of the department

    Returns:
        Dict: Eloomi department
    """
    for d in departments: 
        if departments[d]['name'].lower() == name.strip().lower():
            return departments[d]['id']