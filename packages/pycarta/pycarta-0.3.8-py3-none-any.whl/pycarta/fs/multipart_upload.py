import math

MiB = 1024 ** 2

Maximum_Single_Upload = MiB * 100  # 100 MiB

Estimated_Upload_Speed = MiB * 1  # 1 MiB / s


def worst_case_upload_duration(file_size: int):
    return math.ceil(file_size / Estimated_Upload_Speed)


def calculate_parts(file_size: int):
    return max(1, math.ceil(file_size / Maximum_Single_Upload))


def upload_parameters(file_size: int):
    return calculate_parts(file_size), worst_case_upload_duration(file_size)




