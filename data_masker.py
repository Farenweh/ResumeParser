import re


def mask(content: str, phone_masker="18066666666", email_masker="Weiketong@whut.edu.cn") -> dict:
    # 1匹配电话号码（11位，可能含空格或短横线）
    pattern = r'(?:\d{3}[\s-]?\d{4}[\s-]?\d{4})'
    matches = re.findall(pattern, content)
    phone_numbers = []
    for match in matches:
        phone_numbers.append(re.sub(r'[-\s]', '', match))
        content = re.sub(match, phone_masker, content)

    # 2匹配邮箱
    pattern = r'\w+@[\w.]+\.\w+'
    matches = re.findall(pattern, content)
    emails = []
    for match in matches:
        emails.append(match)
        content = re.sub(match, email_masker, content)

    return {"phone_masker": phone_masker,
            "email_masker": email_masker,
            "phone_numbers": phone_numbers,
            "emails": emails,
            "content_masked": content}


def demask(content: str, resource_masked: dict) -> str:
    # 1复原电话
    for phone_number in resource_masked["phone_numbers"]:
        content = re.sub(resource_masked["phone_masker"], phone_number, content)
    # 2复原邮箱
    for email in resource_masked["emails"]:
        content = re.sub(resource_masked["email_masker"], email, content)

    return content
