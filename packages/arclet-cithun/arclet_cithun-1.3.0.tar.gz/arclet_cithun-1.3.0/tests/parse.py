from arclet.cithun.model import Permission


assert Permission.parse("a=7") == (7, "=", False)
assert Permission.parse("d+vma") == (Permission.VISIT | Permission.MODIFY | Permission.AVAILABLE, "+", True)
assert Permission.parse("av") == (Permission.VISIT, "=", False)
assert Permission.parse("a-m") == (Permission.MODIFY, "-", False)
assert Permission.parse("5") == (5, "=", False)
assert Permission.parse("a") == (Permission.AVAILABLE, "=", False)
