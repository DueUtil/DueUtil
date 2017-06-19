from fun.helpers.misc import DefaultBunch

test_bunch = DefaultBunch(default="Test",test_value = "cheese")
print (test_bunch.test_value)
print (test_bunch["test_value"])
print(test_bunch.apple)
test_bunch.test_value = "lol"
print(test_bunch.test_value)
test_bunch["test_value"] = "kek"
print(test_bunch.test_value)
test_bunch.what_da_fuk = 100
print(test_bunch.what_da_fuk)
test_bunch.what_da_fuk += 123
print(test_bunch.what_da_fuk)
test_bunch.a_value 

"""
player["inventory"]["banners"]
"""
