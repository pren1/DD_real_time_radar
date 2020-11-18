import requests
import pprint
import pdb

contents = requests.get('https://api.vtbs.moe/v1/info').json()
result = []
for single in contents:
    if single['liveStatus'] == 1:
        result.append(single['roomid'])
print(len(result))
pdb.set_trace()

s1 = [21501730,1491028,21302070,21720301,21712857,1191799,22463523,43307,21412734,22319939,7554620]
s2 = [22535566,21362762,21345362,21180272,4637570,7173352,4992290,21718578,596082,8112629,11306]
s3 = [21720308,11312,1625715,1603600,3473293,801580,21564812,7439941,15978,19064,10947031]
s4 = [21927742,671472,22389319,21696957,15536,21302469,236672,22377405,10801,157501,6608174,708397]

# print(f"s1: {len(s1)}, set: {len(set(s1))}")
# print(f"s2: {len(s2)}, set: {len(set(s2))}")
# print(f"s3: {len(s3)}, set: {len(set(s3))}")
# print(f"s4: {len(s4)}, set: {len(set(s4))}")

res = s1 + s2 + s3 + s4
print(f"res: {len(res)}, set: {len(set(res))}")

diff = set(res) - set(result)


def get_difference_between_two_lists(old_list, new_list):
    total_set = set(old_list + new_list)
    removed_list = []
    added_list = []
    for single in total_set:
        if single in old_list and single in new_list:
            continue
        elif single in old_list and single not in new_list:
            removed_list.append(single)
        elif single not in old_list and single in new_list:
            added_list.append(single)
        else:
            assert 1 == 0, "Fatal logic error"
    return removed_list, added_list


remove, add = get_difference_between_two_lists(result, res)
print(remove)
print(add)
pdb.set_trace()